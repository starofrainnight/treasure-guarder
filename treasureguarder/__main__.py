#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Console script for treasure-guarder."""

import click
import shotatlogging
from .treasureguarder import TreasureGuarder


@click.command()
@click.argument("cfg_path", default="./treasure-guarder.yml")
def main(**kwargs):
    """Console script for treasure-guarder.

    CFG_PATH: Configuration file path
    """
    shotatlogging.setup()

    guarder = TreasureGuarder(kwargs)
    guarder.exec_()


if __name__ == "__main__":
    main()
