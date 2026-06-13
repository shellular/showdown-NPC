import os
import subprocess
import asyncio

from funcs import basicFunctionUtil
from funcs import serverLoad

async def main():
    basicFunctionUtil.ping()
    serverLoad.fullHousekeeping()

asyncio.run(main())