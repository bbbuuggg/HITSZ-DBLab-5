import random
from datetime import datetime

import mysql.connector
from flask import session  # 不同界面共享账号密码
from flask import Flask, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 设置应用的密钥
app.secret_key = "keyyyyy"  # 本身应该保密，设置到flask的环境变量里什么的，这里偷懒、

# 设置数据库连接信息
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "X021010x",
    "database": "peeeet",
}

# 将数据库连接信息传递给SQLALCHEMY_DATABASE_URI
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}"


db = SQLAlchemy(app)
# 创建 LoginManager 实例
login_manager = LoginManager(app)
login_manager.login_view = "login"


# 定义用户模型
class User(UserMixin, db.Model):
    name = db.Column(db.String(80), primary_key=True, unique=True)
    password = db.Column(db.String(80))

    # override get_id已确保使用name索引而不是默认的id
    def get_id(self):
        return self.name


class Administrators(db.Model):
    a_id = db.Column(db.String(10), primary_key=True)
    a_name = db.Column(db.String(20))
    a_password = db.Column(db.String(20))


# 宠物信息模型
class Pet(db.Model):
    pet_id = db.Column(db.Integer, primary_key=True)
    breeds_id = db.Column(db.Integer)
    tra_id = db.Column(db.Integer)
    nature_id = db.Column(db.Integer)
    pet_name = db.Column(db.String(100))
    pet_gentle = db.Column(db.String(100))
    birthday = db.Column(db.DateTime, default=datetime.utcnow)  # 日期时间属性
    color = db.Column(db.String(100))


# 申请表模型
class Application(db.Model):
    application_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    pet_id = db.Column(db.Integer)
    add_id = db.Column(db.Integer)
    application_user = db.Column(db.String(20))
    gentle = db.Column(db.String(8))
    age = db.Column(db.String(20))
    phone = db.Column(db.String(100))
    email = db.Column(db.String(100))


# 创建数据库表格
with app.app_context():
    db.create_all()


# 用户加载函数
@login_manager.user_loader
def load_user(user_name):
    # 根据用户 name 加载用户对象，例如从数据库中加载用户
    return User.query.filter_by(name=user_name).first()


# 用户注册
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]
        # 创建用户对象
        user = User(name=name, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


# 用户登录
@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = "请输入你的密码"  # 初始化
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(name=name).first()
        session["username"] = name  # 存储username
        u_name = session.get("username")
        print(u_name)
        # 检查是否是管理员登录
        if user and user.password == password and is_administrator(name, password):
            return redirect(url_for("admin"))
        elif user and user.password == password:
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            error_message = "用户名或密码错误，请重试."

    return render_template("login.html", error_message=error_message)


# 辅助函数，检查是否是管理员登录
def is_administrator(username, password):
    # 查询数据库中的管理员信息
    print(username, password)
    administrator = Administrators.query.filter_by(
        a_name=username, a_password=password
    ).first()
    a = Administrators.query.all()
    print(a)

    # 如果找到匹配的管理员记录，表示是管理员登录
    return administrator is not None


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


### 管理界面
# 领养跟踪表模型
class adoption_tracking(db.Model):
    tra_id = db.Column(db.Integer, primary_key=True)
    a_id = db.Column(db.String(10), comment="管理员ID")
    pet_id = db.Column(db.Integer, comment="宠物ID")
    user_name = db.Column(db.String(255), comment="用户名")
    tra_description = db.Column(db.String(100), comment="跟踪描述")
    tra_time = db.Column(db.String(15), comment="跟踪时间")


# 审核模型
class audit(db.Model):
    application_id = db.Column(db.Integer, primary_key=True)
    a_id = db.Column(db.String(10), primary_key=True)
    result = db.Column(db.String(10))
    reason = db.Column(db.String(100))


# 管理员主页
@app.route("/admin", methods=["GET", "POST"])
def admin():
    username = session.get("username")  # 获取登录界面的管理员账号
    pets = Pet.query.all()  # 获取所有的pet信息
    # print(username)  # 因为a_id不可为none，所以也从防止了直接访问admin页面
    if request.method == "POST":
        if "application" in request.form:
            print("c")
            a_id = get_admin_id(username)
            application_id = request.form.get("application_id")
            application = Application.query.get(application_id)
            approval = request.form.get("approval")
            reason = request.form.get("reason")
            Adoption_tracking = adoption_tracking.query.all()
            # 处理审核操作
            if approval == "approve":
                # 同意申请
                result = "approved"  #
                tra_id = len(Adoption_tracking) + 1
                print("b")
                print(tra_id, a_id, application.pet_id, application.name)
                # 创建 adoption_tracking 实体并插入数据库
                new_tracking = adoption_tracking(
                    tra_id=tra_id,
                    a_id=a_id,
                    pet_id=application.pet_id,
                    user_name=application.name,
                    tra_description="None",
                    tra_time="guess",
                )
                db.session.add(new_tracking)
                # 提交会话以保存更改到数据库
                db.session.commit()
            elif approval == "reject":
                # 拒绝申请
                result = "rejected"
            Audit = audit(
                application_id=application_id, a_id=a_id, result=result, reason=reason
            )
            # 将udit对象添加到数据库会话
            db.session.add(Audit)

            # 提交会话以保存更改到数据库
            db.session.commit()

        elif "add_pet" in request.form:
            pet_id = len(pets) + 1
            pet_name = request.form.get("pet_name")
            pet_gentle = request.form.get("pet_gentle")
            breeds_id = request.form.get("breeds_id")
            tra_id = (
                int(request.form.get("tra_id"))
                if request.form.get("tra_id") != "0"
                else None
            )
            nature_id = request.form.get("nature_id")
            birthday = request.form.get("birthday")
            color = request.form.get("color")
            # 创建 Pet 对象并设置所有属性
            new_pet = Pet(
                pet_id=pet_id,
                pet_name=pet_name,
                pet_gentle=pet_gentle,
                breeds_id=breeds_id,
                tra_id=tra_id,
                nature_id=nature_id,
                birthday=birthday,
                color=color,
            )
            db.session.add(new_pet)
            db.session.commit()
        if "edit_pet" in request.form:
            pet_id = request.form.get("pet_id")
            change_name = request.form.get("change_name")
            change_thing = request.form.get("change_thing")

            # 查询要修改的宠物
            pet = Pet.query.get(pet_id)
            if pet:
                # 根据 change_name 确定要修改的属性
                if change_name == "宠物名称":
                    pet.pet_name = change_thing
                elif change_name == "宠物性别":
                    pet.pet_gentle = change_thing
                elif change_name == "性格ID":
                    pet.nature_id = change_thing
                elif change_name == "宠物生日":
                    pet.birthday = change_thing
                elif change_name == "宠物颜色":
                    pet.color = change_thing

                # 保存修改到数据库
                db.session.commit()

        elif "delete_pet" in request.form:
            # 处理删除宠物信息的逻辑
            pet_id = request.form.get("delete_pet_id")
            print("try to delete your trash")
            # 查询要删除的宠物
            pet = Pet.query.get(pet_id)
            if pet:
                # 从数据库中删除宠物
                db.session.delete(pet)
                db.session.commit()
    # 查询待审核的领养申请
    pending_requests = Application.query.all()
    print("a")
    # 再次查询所有宠物信息
    pets = Pet.query.all()
    return render_template("admin.html", applications=pending_requests, pets=pets)


# 通过用户名询管理员
def get_admin_id(username):
    administrator = Administrators.query.filter_by(a_name=username).first()

    if administrator:
        return administrator.a_id
    else:
        return None


# 用户界面：宠物信息展示/领养申请
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    pets = Pet.query.all()
    if request.method == "POST":
        # 处理用户提交的领养申请，保存到数据库
        pet_id = request.form["pet_id"]
        name = request.form["name"]
        add_id = request.form["add_id"]
        application_user = request.form["application_user"]
        gentle = request.form["gentle"]
        age = request.form["age"]
        phone = request.form["phone"]
        email = request.form["email"]

        # 生成一个5位的随机整数作为application_id
        application_id = random.randint(10000, 99999)
        # 创建一个新的Application对象并设置属性
        application = Application(
            application_id=application_id,
            name=name,
            pet_id=pet_id,
            add_id=add_id,
            application_user=application_user,
            gentle=gentle,
            age=age,
            phone=phone,
            email=email,
        )

        # 将Application对象添加到数据库会话
        db.session.add(application)

        # 提交会话以保存更改到数据库
        db.session.commit()

        return redirect(url_for("dashboard"))
    return render_template("dashboard.html", pets=pets)  # , pets=pets


@app.route("/")  # app.route相当于路由的映射，“/”即为根目录映射时执行的命令
def index():
    return redirect("login")


if __name__ == "__main__":
    app.run(debug=True)
