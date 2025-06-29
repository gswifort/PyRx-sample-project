from pyrx import Db, Ed, command

from .rect import create_rectangle


@command(name="PYRECT")
def _():
    status, width = Ed.Editor.getDouble(
        "\nWidth: ",
        Ed.PromptCondition(Ed.PromptCondition.eNoEmpty | Ed.PromptCondition.eNoNegitive),
    )
    if not status == Ed.PromptStatus.eOk:
        return
    status, height = Ed.Editor.getDouble(
        "\nHeight: ",
        Ed.PromptCondition(Ed.PromptCondition.eNoEmpty | Ed.PromptCondition.eNoNegitive),
    )
    if not status == Ed.PromptStatus.eOk:
        return
    status, center = Ed.Editor.getPoint("\nCenter: ")
    if not status == Ed.PromptStatus.eOk:
        return
    status, rotation = Ed.Editor.getAngle(center, "\nRotation: ")
    if not status == Ed.PromptStatus.eOk:
        return
    rect = create_rectangle(width, height, center, rotation)
    Db.curDb().addToCurrentspace(rect)
