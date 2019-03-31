
class Client_Obj(object):
    def __init__(self):
        # define
        self.USR_NON_EXISTENT = "account non-existent"
        self.USR_PASSWORD_ERROR = "password error"
        self.USR_PASS = "check ok"

        self.usr_account = None
        self.usr_password = None
        self.usr_authority = None
        # 临时网络通信密匙


        # 客户端类型,每次注册的时候 可以修改,和绑定拖拉机
        self.client_type = None

        # 与服务器的SID
        self.network_sid = None
        # 与服务器通信的通道,名字为SID
        self.network_room = None
        # 公共推送通道,自己为房主
        self.public_own_room = None
        # 与客户端的私密通道
        self.private_client_room = None
        # 订阅公共服务器推送通道
        self.sub_server_room = None
        # 订阅的公共消息,自己为listener
        self.sub_public_room = []

    # 设置账户
    def get_usr_account(self):
        return self.usr_account
    def set_usr_account(self,arg_account):
        self.usr_account = arg_account

    # 设置密码
    def get_usr_password(self):
        return self.usr_password
    def set_usr_password(self,arg_password):
        self.usr_password = arg_password

    # 验证账户
    def check_usr(self,account,password):
        if self.usr_account == account:
            if self.usr_password == password:
                return  self.USR_PASS
            else:
                return self.USR_PASSWORD_ERROR
        else:
            return self.USR_NON_EXISTENT

    # 网络通信的SID
    def set_network_sid(self,sid):
        self.network_sid = sid
    def get_network_sid(self):
        return  self.network_sid

    # 客户端类型
    def set_client_type(self,type):
        self.client_type = type
    def get_client_type(self,type):
        return self.client_type

    # 与服务器通信的通道,名字为SID
    def set_network_room(self,room_num):
        self.network_room = room_num
    def get_network_room(self):
        return self.network_room

    # 公共推送通道,自己为房主
    def set_public_own_room(self,room_num):
        self.public_own_room = room_num
    def get_public_own_room(self):
        return self.public_own_room

    # 与客户端的私密通道
    def set_private_client_room(self,room_num):
        self.private_client_room = room_num
    def get_private_client_room(self):
        return self.private_client_room

    # 订阅公共服务器推送通道
    def set_sub_server_room(self,room_num):
        self.sub_server_room = room_num
    def get_sub_server_room(self):
        return self.sub_server_room

    # 订阅的公共消息池
    def set_sub_public_room(self,room_num):
        if room_num not in self.sub_public_room:
            self.sub_public_room.append(room_num)
        else:
            print('room has exite')
            return
    def get_sub_public_room(self):
        return self.sub_public_room
    def remove_sub_public_room(self,room_num):
        if room_num in self.sub_public_room:
            self.sub_public_room.remove(room_num)
        else:
            print('room has not exite ')
    def clear_sub_public_room(self):
        self.sub_public_room.clear()