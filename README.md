# PyRx-based Sample Project

A sample project based on PyRx. This project is created for PyRx users, but most of its elements can be used to create a project not based on PyRx. You might feel that I describe overly simple things in many places, but I want this project to help someone completely new get started. Note: Do not treat this project and its elements as "best practices"; I don't even know if they are good practices, but they are the best ones I know :)

## Project Structure

The basic structure of a Python project looks as follows ([commit](https://github.com/gswifort/PyRx-sample-project/tree/6eac1853dfa88c42a7605636efe3f82a8bc270b8)):

```raw
.
├── .git
├── src/
│   └── pyrx_sample_project/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Virtual Environment

It is recommended to create each project in a separate virtual environment. In the project directory, execute:

```bash
$ python -m venv venv
$ venv\Scripts\activate.bat
(venv) $ python -V
Python 3.12.7  # ensure the virtual environment has the correct Python version
```

This will create and activate a virtual environment - the console prompt will display ``(venv)`` before the path.

To install the required dependencies (in our case ``cad-pyrx``), execute the following command within the virtual environment:

```bash
python -m pip install -e .[dev]
```

This command will install our package in editable mode. You need to run this command every time new dependencies are added to the project.

## Sample Module

([commit](https://github.com/gswifort/PyRx-sample-project/tree/8bc8e8b07078c4b82c0429854e683ddf7c7972ef))

For demonstration purposes, we will create a module ``rect.py`` with the function ``create_rectangle`` and a module ``cmds.py`` adding the command ``PYRECT``:

[rect.py](https://github.com/gswifort/PyRx-sample-project/blob/1c293f7041477b2d95d197a3345f94d643131f81/src/pyrx_sample_project/rect.py)  
[cmds.py](https://github.com/gswifort/PyRx-sample-project/blob/1c293f7041477b2d95d197a3345f94d643131f81/src/pyrx_sample_project/cmds.py)

Additionally, we will create tests:

[test_rect.py](https://github.com/gswifort/PyRx-sample-project/blob/1c293f7041477b2d95d197a3345f94d643131f81/tests/test_rect.py)

We also need to add a module to run the tests:

[testrunner.py](https://github.com/gswifort/PyRx-sample-project/blob/1c293f7041477b2d95d197a3345f94d643131f81/testrunner.py)

This module will add the ``RUN_TESTS`` command after being loaded into CAD.

To ensure the ``testrunner.py`` module loads automatically into the CAD application, we need to add a file ``pyrx_onload.py`` in the project directory:

[pyrx_onload.py](https://github.com/gswifort/PyRx-sample-project/blob/1c293f7041477b2d95d197a3345f94d643131f81/pyrx_onload.py)

## Running the CAD Application

For development purposes, the best way to run the host application seems to be using the command line. In the virtual environment, execute:

```bash
zwcad /ld venv\Lib\site-packages\pyrx\RxLoaderZ25.0.zrx
```

- Specify the name of the host application if its exe file is in the search path or provide the full path to the CAD application's exe file,
- Provide the path to the ``RxLoader`` file appropriate for your CAD application,
- In AutoCAD, you may also need to specify the ``/six`` parameter in the command line.

## Distribution

([commit](https://github.com/gswifort/PyRx-sample-project/tree/1c293f7041477b2d95d197a3345f94d643131f81))

In this tutorial, we treat our package as the "final product." However, if we wanted to distribute our package as a library installable via ``pip``, we would need to build a ``whl`` distribution. To do this, execute:

```bash
(venv) > python -m build
```

The ``.whl`` (and ``.tar.gz``) files will be placed in the ``dist`` directory.

As mentioned earlier, we treat our package as the final product, so we will want to create an installer. I use an SFX archive for this purpose. It is not the simplest approach but probably the most flexible.

The process is as follows:

- Build an exe file based on the SFX archive using the ``build_setup.py`` module. This module:
  - Builds the ``whl`` distribution of our package,
  - Creates an archive containing the files:
    - setup.bat,
    - bootstrap.py,
    - loader.lsp,
    - loader.py,
- When the exe file is run on the user's computer, the archive will unpack into a temporary directory and execute the ``setup.bat`` file,
- The ``setup.bat`` file:
  - Installs Python (if it doesn't exist) in a global location (`%localappdata%\Programs\Python\Python312`),
  - Executes the ``bootstrap.py`` file located in the archive,
- The `bootstrap.py` file:
  - Creates an installation directory,
  - Installs our package from the `.whl` file along with dependencies,
  - Copies the `loader.py` file,
  - Creates the `loader.lsp` file,
- The ``loader.lsp`` file should be added to the list of scripts executed at the start of the CAD application. This script:
  - Loads the appropriate version of the PyRx module,
  - Loads the ``loader.py`` file,
- The ``loader.py`` file:
  - Adds our installation directory to Python's search path (``sys.path``),
  - Loads the commands (``cmds.py`` module).
