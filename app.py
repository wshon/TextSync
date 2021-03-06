import asyncio
import copy
import hashlib  # 导入功能模块，此模块有MD5,SHA1,SHA256等方法

import aiohttp_jinja2
import jinja2
from aiohttp import web
from aiohttp_sse import sse_response

m = hashlib.md5()  # 声明一个对象
sync_group = {

}


async def text_sync(request):
    sync_id = request.match_info['uuid']
    # loop = request.app.loop
    async with sse_response(request) as resp:
        if sync_id not in sync_group:
            sync_group[sync_id] = []
        sync_group[sync_id].append(resp)
        await resp.send("Connect Success.")
        while True:
            # data = 'Text Sync Addr: {}'.format(datetime.now())
            # print(data)
            # await resp.send(data)
            # await asyncio.sleep(10, loop=loop)
            await asyncio.sleep(10)
    # return resp


async def text_send(request):
    sync_id = request.match_info['uuid']
    post_data = await request.json()
    text = post_data['text']
    if sync_id not in sync_group:
        return web.HTTPNotFound()
    sync_list = copy.copy(sync_group[sync_id])
    for sync in sync_list:
        try:
            await sync.send(text)
        except ConnectionResetError:
            sync_group[sync_id].remove(sync)
    return web.json_response({'code': 0})


@aiohttp_jinja2.template('index.html')
async def sync(request):
    sync_id = request.match_info['uuid']
    sync_id = hashlib.md5(sync_id.encode()).hexdigest()
    return {'sync_id': sync_id}


@aiohttp_jinja2.template('index.html')
async def index(request):
    return {'name': 'Andrew', 'surname': 'Svetlov'}


app = web.Application()
aiohttp_jinja2.setup(app,
                     loader=jinja2.FileSystemLoader('./templates'))
app.router.add_route('GET', '/', index)
app.router.add_route('GET', '/{uuid}', sync)
app.router.add_route('GET', '/sync/{uuid}', text_sync)
app.router.add_route('POST', '/send/{uuid}', text_send)
app.router.add_static('/static', './static')

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=8080)
