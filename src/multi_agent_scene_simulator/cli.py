import asyncio
import click
from .services import executor

@click.group()
def cli():
    pass

@cli.command()
@click.argument("scene_requirement")
def run(scene_requirement: str):
    asyncio.run(executor.execute(scene_requirement))


if __name__ == "__main__":
    cli()
