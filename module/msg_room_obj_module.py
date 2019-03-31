# 消息房间
class Msg_Room(object):
    def __init__(self,owner):
        self.owner = owner
        self.admin = []
        self.normal_usr = []
        self.tag = []
        self.area = None

    # 房间拥有者
    def set_room_owner(self,owner):
        self.owner = owner
    def get_room_owner(self):
        return self.owner

    # 房间管理员
    def set_room_admin(self,admin):
        self.admin.append(admin)
    def get_room_admin(self):
        return self.admin
    def delate_room_admin(self,admin):
        if admin in self.admin:
            self.admin.remove(admin)
            return True
        else:
            return False
    # 普通用户
    def set_normal_usr(self,usr):
        self.normal_usr.append(usr)
    def get_normal_usr(self):
        return self.normal_usr
    def delate_normal_usr(self,usr):
        if usr in self.normal_usr:
            self.normal_usr.remove(usr)
            return True
        else:
            return False

    # 房间标签
    def set_room_tag(self,tag):
        self.tag.append(tag)
    def get_room_tag(self):
        return self.tag
    def clean_room_tag(self):
        self.tag.clear()

    # 房间所属于的区域
    def set_room_area(self,area):
        self.area = area
    def get_room_area(self):
        return  self.area