from flask import Flask, render_template
from flask_socketio import SocketIO,Namespace, emit
from flask_socketio import join_room, leave_room
import flask
import json

from module.client_obj_module  import Client_Obj
from module.msg_room_obj_module import Msg_Room
from module.convert_to_pdf_module import KPrint

from data.server_mysql.server_mysql import sqlHelper

import types
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
M_WEBSOCKET_RESPONSE='response'
mysqlHelper = sqlHelper("localhost", 3306, "root", "123456", "tractor", "map_tractor")



# 公共消息推送通道,自己为房主
ROOM_TYPE_OWN_PUSH_ROOM = 1
# 与客户端之间的私有通道
ROOM_TYPE_OWN_PRIVATE_CLIENT_ROOM = 2
# 属于服务器的推送通道,每个客户端都要订阅
ROOM_TYPE_SERVER_PUSH_ROOM = 3

@app.route('/')
def index():
    return render_template('index.html')



# 消息房间管理器
class Msg_Room_Manager(object):
    def __init__(self,arg_socket_io_emit, arg_join_room, arg_leave_room):
        # 包发送
        self.m_socke_io_emit = arg_socket_io_emit
        self.m_join_room = arg_join_room
        self.m_leave_room = arg_leave_room

        # 房间管理器
        self.room_pool={}
        self.room_num = 0




    # 创建房间
    def create_new_room(self,owner,type):
        # 创建房间号
        temp_room_num = self.create_room_num()
        # 创建房间
        self.room_pool[temp_room_num] = Msg_Room(owner)
        # 该用户加入房间
        self.m_join_room(temp_room_num, sid=owner.get_network_sid())

        # 设置该用户的属性: 属于自己的房间
        if type == ROOM_TYPE_OWN_PUSH_ROOM:
            owner.set_public_own_room(temp_room_num)
        elif type == ROOM_TYPE_OWN_PRIVATE_CLIENT_ROOM:
            owner.set_private_client_room(temp_room_num)
        elif type == ROOM_TYPE_SERVER_PUSH_ROOM:
            print('serer room has create')
        return temp_room_num

    # 创建房间号
    def create_room_num(self):
        self.room_num += 1
        return self.room_num

    # 房间中查看房主
    def get_room_owner(self,room_num):
        if room_num in self.room_pool.keys():
            return self.room_pool[room_num].get_room_owner()
        else:
            print('the room has not exite')
            return None

    # 房间中设置房主
    def set_room_owner(self,room_num,owner):
        if room_num in self.room_pool.keys():
            self.room_pool[room_num].set_room_owner(owner)
            self.m_join_room(room_num, sid=owner.get_network_sid())
            owner.set_public_own_room(room_num)
            return True
        else:
            print('the room has not exite')
            return False

    #------------------------------------------------ 系统属性
    # 房间中查看管理员
    def get_room_admin(self,room_num):
        if room_num in self.room_pool.keys():
            return self.room_pool[room_num].get_room_admin()
        else:
            print('the room has not exite')
            return None
    # 房间中添加管理员
    def add_room_admin(self,room_num,admin):
        if room_num in self.room_pool.keys():
            self.room_pool[room_num].set_room_admin(admin)
            self.m_join_room(room_num,sid=admin.get_network_sid())
            # 这是系统属性
            return True
        else:
            print('the room has not exite')
            return False

    # 房间中删除管理员
    def delate_room_admin(self,room_num,admin):
        if room_num in self.room_pool.keys():
            self.m_leave_room(room_num,sid=admin.get_network_sid())
            return self.room_pool[room_num].delate_room_admin(admin)
        else:
            print('the room has not exite')
            return False
    #----------------------------------------------



    # 房间中查看普通用户
    def get_normal_usr(self,room_num):
        if room_num in self.room_pool.keys():
            return self.room_pool[room_num].get_normal_usr()
        else:
            print('the room has not exite')
            return None

    # 房间中添加普通用户
    def add_normal_usr(self,room_num,usr):
        if room_num in self.room_pool.keys():
            if usr not in self.room_pool[room_num].get_normal_usr():
                # 用户的订阅列表添加房间号
                usr.set_sub_public_room(room_num)
                # 该房间号添加该用户
                self.room_pool[room_num].set_normal_usr(usr)
                self.m_join_room(room_num, sid=usr.get_network_sid())
            else:
                print('usr has exite')
            print('sub sucess')
            return True
        else:
            print('sub error: room has not exite')
            return False

    # 房间中删除普通用户
    def delate_normal_usr(self,room_num,usr):
        if room_num in self.room_pool.keys():
            if usr in self.room_pool[room_num].get_normal_usr():
                if room_num in usr.get_sub_public_room():
                    # 用户的订阅列表删除房间号
                    usr.remove_sub_public_room(room_num)
                    self.m_leave_room(room_num,sid=usr.get_network_sid())
                    self.room_pool[room_num].delate_normal_usr(usr)
                    return True
                else:
                    print('usr has not sub the room')
                    return False
            else:
                print('the room has not the usr')
                return False
        else:
            print('the room has not exite')
            return False

    # 消息发送
    def broadcase_room(self,room_num,sender,msg):
        if room_num in self.room_pool.keys():
            # 如果是房主或者管理员,才能广播消息
            if self.room_pool[room_num].get_room_owner() == sender or sender in self.room_pool[room_num].get_room_admin():
                print('braoid sucess')
                self.m_socke_io_emit(M_WEBSOCKET_RESPONSE, msg, room=room_num)
        else:
            print('the room has not exite')
            return False

class CLient_Manager(object):
    def __init__(self):
        # ID池
        self.new_sid_index = 0
        self.new_sid_pool=[]
        # 所有客户端
        self.client_pool = {}
        # 数据推送客户端
        self.pusher_client_pool = {}
        # 数据接收客户端
        self.receiver_client_pool = {}
        # 房间管理器
        self.room_manager = Msg_Room_Manager(emit,join_room,leave_room)

    # 添加推送者到客户端池
    def add_pusher_client(self,new_client):

        if new_client.get_network_sid() in self.pusher_client_pool.keys():
            print('已经添加了客户端')
        else:
            new_client.set_client_type("pusher")
            self.pusher_client_pool[new_client.get_network_sid()] = new_client
            public_room = self.room_manager.create_new_room(new_client,ROOM_TYPE_OWN_PUSH_ROOM)
            private_client_room = self.room_manager.create_new_room(new_client,ROOM_TYPE_OWN_PRIVATE_CLIENT_ROOM)
            print(public_room)
            print(private_client_room)

    # 获取推送者
    def get_pusher_client(self):
        return self.pusher_client_pool

    # 添加接收者到客户端池
    def add_receiver_client(self,new_client):
        new_client.set_client_type("receiver")
        self.receiver_client_pool[new_client.get_network_sid()] = new_client
    # 获取接收者
    def get_receiver_client(self):
        return self.receiver_client_pool
    def find_client_from_sid(self,sid):
        if sid in self.client_pool.keys():
            print('sid find client')
            return self.client_pool[sid]
        else:
            print('the client has not exite')
            return None
    # 添加客户端
    def add_client(self, new_client,new_sid):
        new_client.set_network_sid(new_sid)
        self.client_pool[new_sid] = new_client
        return new_sid  #111111
    # 删除客户端
    def delete_client(self,sid):
        if sid in self.client_pool:
            del self.client_pool[sid]
            # 如果是在推送者中
            if sid in self.pusher_client_pool.keys():
                del self.pusher_client_pool[sid]
            if sid in self.receiver_client_pool.keys():
                del self.receiver_client_pool[sid]
            return True
        else:
            print('the client has not exite')

    # 推送者推送数据
    def pusher_post_data(self,usr,data):
        # 获得私有的房间号
        m_room_num = usr.get_public_own_room()
        self.room_manager.broadcase_room(m_room_num,usr,data)

    # 添加普通用户到指定房间号
    def add_usr_to_room(self,room_num,usr):
        self.room_manager.add_normal_usr(room_num,usr)
    # 普通用户从指定房间号删除
    def remove_usr_from_room(self,room_num,usr):
        self.room_manager.delate_normal_usr(room_num,usr)


    # 私有通道,直接提升为管理员 可以双向通信
    def sub_private_client(self,room_num,usr):
        # 获得私有的房间号
        own = self.room_manager.get_room_owner(room_num)
        private = own.get_private_client_room()
        usr.set_private_client_room(private)
        print(private)
        self.room_manager.add_room_admin(private,usr)
    def sent_msg_to_private_client(self,usr):
        room = usr.get_private_client_room()
        self.room_manager.broadcase_room(room, usr, {'data': 'from other client'})





client_manager = CLient_Manager()
kprint = KPrint()

class M_WebSocketNamespace(Namespace):

    # 注册发送函数,和加入房间函数,离开房间函数
    def init(self,arg_socket_io_emit,arg_join_room,arg_leave_room):
        self.m_socke_io_emit = arg_socket_io_emit
        self.m_join_room = arg_join_room
        self.m_leave_room = arg_leave_room

        self.m_network_private_key = None
        self.index = 5

    # 连接成功
    def on_connect(self):
        print('Client connect')
        #self.m_socke_io_emit(M_WEBSOCKET_RESPONSE, {'data': 'Connected'})

    # 客服端断开连接
    def on_disconnect(self):
        if client_manager.delete_client(flask.request.sid):
            print('client del ok')
        else:
            print('client del error')
        print('Client disconnected')

    # 获得ID
    def on_get_private_key(self,data):
        self.m_client = Client_Obj()
        print('get id OK')
        # 产生ID
        self.m_network_private_key = client_manager.add_client(self.m_client,flask.request.sid)

        self.index += 1

        # 添加到客服端管理器
        #msg = data['data']
        type = data['senderType']
        if type == 'pusher':
            print('this is pusher')
            client_manager.add_pusher_client(self.m_client)
        elif type == 'receiver':
            client_manager.add_receiver_client(self.m_client)
            print('this is receiver')
        jsonTypeMessage = {
            "status":{
                "responseCode": 200,
                "responseInfo": "OK"
            },
            "abstract": {
                "senderType": "sever",
                "msgType": "response",
                "cmdName": "getKey",
                "packageIndex": 0,
                "privateKey": ""
            },

            "data": {
                "key": self.m_network_private_key,
            }
        }

        self.m_socke_io_emit(M_WEBSOCKET_RESPONSE, jsonTypeMessage)

    # 获取推送者
    def on_get_pusher(self,data):
        pusher_len = len(client_manager.get_pusher_client())
        print('pusher num:'+str(pusher_len))
        resMsg = {}
        resMsg['client_num'] = pusher_len
        pusherMsg = {}
        pusher_pool = client_manager.get_pusher_client()
        index = 0
        for key in pusher_pool:
            rom_num = pusher_pool[key].get_public_own_room()
            index += 1
            pusherMsg_item_index = "pusherMsg%d" % index
            pusherMsg[pusherMsg_item_index] = rom_num
        resMsg['pusherMsg']=pusherMsg

        self.m_socke_io_emit(M_WEBSOCKET_RESPONSE, {'data':resMsg})
    # 订阅推送者
    def on_sub_pusher(self,data):
        data= data['data']
        room_num = data['type']
        print('this is sub num:'+str(room_num))
        client = client_manager.find_client_from_sid(flask.request.sid)
        if client != None:
            client_manager.add_usr_to_room(room_num,client)
        else:
            print('本用户不存在')

    # 推送者推送数据
    def on_post_data(self,data):
        print('pl')
        client = client_manager.find_client_from_sid(flask.request.sid)
        if client != None:
            client_manager.pusher_post_data(client,data)
        else:
            print('本用户不存在')

    def on_sub_private_client(self,data):
        data = data['data']
        room_num = data['type']
        print('this is sub num:' + str(room_num))
        client = client_manager.find_client_from_sid(flask.request.sid)
        if client != None:
            client_manager.sub_private_client(room_num,client)
        else:
            print('本用户不存在')

    def  on_sent_msg_private_client(self, data):
        client = client_manager.find_client_from_sid(flask.request.sid)
        if client != None:
            client_manager.sent_msg_to_private_client(client)
        else:
            print('本用户不存在')

    def on_edit_msg(self,data):
        msg = data['data']
        html_content = msg['html']

        body = """
            <html>
              <head>
              <meta charset="UTF-8">
              </head>
              <body>
              """ +html_content+"""
              </body>
              </html>
            """
        print(body)
        kprint.print_from_str(body, r'home\usr\notify_pdf\body.pdf')

    # 广播命名空间内的客户端
    def on_broadcast_all(self, data):
        print('broadcase')
        self.m_socke_io_emit(M_WEBSOCKET_RESPONSE, {'data': data['data']}, broadcast=True)

    def on_response(self, data):
        print('get message')
        self.message_parse(data)

    def message_parse(self, data):
        #frame = json.loads(data)
        print(data)

        if data['abstract']['senderType'] == 'receiver':
            self.receiver_message_parse(data)
        elif data['abstract']['senderType'] == 'pusher':
            self.pusher_message_parse(data)

    def receiver_message_parse(self, frame):
        if frame['abstract']['cmdName'] == 'tractorMapAsk':
            self.push_tractor_map()
        elif frame['abstract']['cmdName'] == 'tractorMeterAsk':
            self.push_tractor_meter()
        elif frame['abstract']['cmdName'] == 'tractorWarningAsk':
            self.push_tractor_warning()
        elif frame['abstract']['cmdName'] == 'tractorRouteAsk':
            self.push_tractor_route()
        elif frame['abstract']['cmdName'] == 'tractorStatisticalAsk':
            self.push_tractor_statistical()

    def pusher_message_parse(self, frame):
        print(frame)
        if frame['abstract']['cmdName'] == "getKey":
            self.on_get_private_key(frame['abstract'])
        elif frame['abstract']['cmdName'] == "pushMap":
            pass

    def push_tractor_warning(self):
        #mysqlHelper.creat_mysql()
        mysqlHelper.add_warning_information(20190202, 42, 1, "发动机过热", "请更换发动机")
        #mysqlHelper.delete_warning_information(1)

        information = mysqlHelper.get_warning_information()

        message = {
            "abstract": {
                "senderType": "sever",
                "msgType": "response",
                "cmdName": "tractorWarningPush",
            },
            "data": {
                "warningData": {
                    "quantity": len(information['serial']),
                    "serial": information['serial'],
                    "time": information['time'],
                    "id": information['id'],
                    "level": information['level'],
                    "title": information['title'],
                    "content": information['content']
                }
            }
        }
        self.m_socke_io_emit(M_WEBSOCKET_RESPONSE, message)

    def push_tractor_meter(self):
        pass

    def push_tractor_route(self):
        pass

    def push_tractor_statistical(self):

        #mysqlHelper.add_statistical_information(5, 32, 44, "西华")
        #mysqlHelper.delete_statistical_information(5)
        information = mysqlHelper.get_statistical_information()
        message = {
            "abstract": {
                "senderType": "sever",
                "msgType": "response",
                "cmdName": "tractorStatisticalPush",

            },

            "data": {
                "statisticalData": {
                    "quantity": len(information['id']),
                    "tractorNum": information['id'],
                    "region": information['region'],
                    "frequency": information['frequency'],
                    "time": information['time'],
                    "warning": [20, 50, 10, 2, 3, 6]
                }
            }
        }

        self.m_socke_io_emit(M_WEBSOCKET_RESPONSE, message)

    def push_tractor_map(self):
        information = mysqlHelper.get_map_information()

        '''
        message = {
            "abstract": {
                "senderType": "sever",
                "msgType": "response",
                "cmdName": "tractorMapPush",
            },

            "data": {
                "map": {
                    "provinceQuantity": information['provinceQuantity'],
                    "provinceName": information['provinceName'],
                    "provinceZoom": information['provinceZoom'],
                    "provinceLongitude": information['provinceLongitude'],
                    "provinceLatitude": information['provinceLatitude'],
                    "cityQuantity": information['cityQuantity'],
                    "cityName": information['cityName'],
                    "cityZoom": information['cityZoom'],
                    "cityLongitude": information['cityLongitude'],
                    "cityLatitude": information['cityLatitude'],
                    "tractorQuantity": information['tractorQuantity'],
                    "serialNum": information['serialNum'],
                    "longitude": information['tractorLongitude'],
                    "latitude": information['tractorLatitude'],
                }
            }
        } 
        '''

        message = {
            "abstract": {
                "senderType": "sever",
                "msgType": "response",
                "cmdName": "tractorMapPush",
            },

            "data": {
                "map": {
                    "provinceQuantity": information['provinceQuantity'],
                    "provinceName": information['provinceName'],
                    "provinceZoom": information['provinceZoom'],
                    "provinceLongitude": information['provinceLongitude'],
                    "provinceLatitude": information['provinceLatitude'],
                    "cityQuantity": information['cityQuantity'],
                    "cityName": information['cityName'],
                    "cityZoom": information['cityZoom'],
                    "cityLongitude": information['cityLongitude'],
                    "cityLatitude": information['cityLatitude'],
                    "tractorQuantity": information['tractorQuantity'],
                    "serialNum": information['serialNum'],
                    "longitude": information['tractorLongitude'],
                    "latitude": information['tractorLatitude'],
                    "deviceType": ["CL904型轮式拖拉机", "CL902型轮式拖拉机", "CL904型轮式拖拉机", "CL902型轮式拖拉机", "CL904型轮式拖拉机",
                                   "CL904型轮式拖拉机", "CL804型轮式拖拉机"],
                    "brand": ["东风", "东风", "吉利", "东风", "红旗", "东风", "吉利"],
                    "producer": ["一汽", "二汽", "一汽", "三菱", "三一", "一汽", "一汽"],
                    "serviceProvider": ["川龙", "川龙", "川龙", "川龙", "万盛", "万盛", "万盛"],
                    "deviceTypeQuantity": 3,
                    "deviceTypePool": ["CL904型轮式拖拉机", "CL902型轮式拖拉机", "CL804型轮式拖拉机"],
                    "brandQuantity": 3,
                    "brandPool": ["东风", "吉利", "红旗"],
                    "producerQuantity": 4,
                    "producerPool": ["二汽", "一汽", "三菱", "三一"],
                    "serviceProviderQuantity": 2,
                    "serviceProviderPool": ["川龙", "万盛"]

                }
            }
        }
        self.m_socke_io_emit(M_WEBSOCKET_RESPONSE, message)

if __name__ == '__main__':


    mysqlHelper.connect_mysql()

    websocket = M_WebSocketNamespace('/dashboard')
    websocket.init(emit,join_room,leave_room)
    socketio.on_namespace(websocket)
    socketio.run(app ,host = '0.0.0.0')
