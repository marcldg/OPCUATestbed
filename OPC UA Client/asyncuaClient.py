import asyncio
import sys
import datetime
# sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')


async def main():
    url = 'opc.tcp://localhost:4840/freeopcua/server/'
    # url = 'opc.tcp://commsvr.com:51234/UA/CAS_UA_Server'
    async with Client(url=url) as client:
        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        # Node objects have methods to read and write node attributes as well as browse or populate address space
        _logger.info('Children of root are: %r', await client.nodes.root.get_children())

        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        while True:
            # get a specific node knowing its node id
            timeT1param = client.get_node(ua.NodeId(2, 2))
            timeT1 = await timeT1param.read_value()
            print(type(timeT1))


if __name__ == '__main__':
    asyncio.run(main())