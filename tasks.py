import pathlib

import yaml
from invoke import tasks
from invoke.context import Context

SECRETS = pathlib.Path('secrets.yaml')


# create task to update vscode
@tasks.task
def update_vscode(context: Context):
    password: str = _read_secrets()['password']

    cmd_clone_repo = (
        "git clone https://aur.archlinux.org/visual-studio-code-insiders-bin.git"
    )
    context.run(command=cmd_clone_repo)
    repo_path = pathlib.Path("visual-studio-code-insiders-bin")
    with context.cd(path=repo_path):
        context.run(command="echo 'Y' | makepkg -si")
        context.sudo(command="pacman -U", password=password)
    context.sudo(command="rm -rf ./visual-studio-code-insiders-bin", password=password)


def _read_secrets() -> dict[str, str]:
    return yaml.load(stream=SECRETS.read_text(), Loader=yaml.SafeLoader)
