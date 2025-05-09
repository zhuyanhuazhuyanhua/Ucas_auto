# `user_management` 用户管理系统

一个基于 Django 和 Django REST Framework 的用户管理系统，支持注册、登录、登出、个人信息管理、兴趣管理和权限控制等功能。

---

## 📋 目录

- [技术栈](#技术栈)
- [功能模块](#功能模块)
- [API 接口](#api-接口)
- [数据库设计](#数据库设计)
- [环境配置](#环境配置)
- [使用说明](#使用说明)

---

## ⚙️ 技术栈

| 技术         | 版本        |
|--------------|-------------|
| Django       | 4.2.0       |
| DRF          | 3.14.0      |
| JWT 认证     | SimpleJWT   |
| 数据库       | MySQL       |
| 邮件发送     | SMTP 协议   |

---

## 🧩 功能模块

### ✅ 用户认证
- **注册**：邮箱注册 + 激活邮件发送（SMTP验证邮箱存在性）
- **登录**：JWT Token 认证
- **登出**：Token 加入黑名单

### 🧑‍💻 个人信息管理
- 修改用户名和头像
- 修改密码（旧密码验证）

### 💬 兴趣管理
- 展示兴趣（随机展示最多10个）
- 更新兴趣（支持通过 ID 或名称更新）

### 🔐 权限管理
- 支持用户组和权限分配
- 自定义认证后端（支持邮箱登录）

---

## 🌐 API 接口

| 方法 | 路径                     | 描述                   |
|------|--------------------------|------------------------|
| POST | `/api/users/`            | 注册                   |
| POST | `/api/users/login/`      | 登录                   |
| POST | `/api/users/logout/`     | 登出                   |
| PUT  | `/api/users/update_profile/` | 更新用户名和头像    |
| POST | `/api/users/change_password/` | 修改密码            |
| GET  | `/api/users/showinterest/` | 展示用户兴趣         |
| POST | `/api/users/update_interests/` | 更新用户兴趣       |
| GET  | `/api/interests/`        | 获取所有兴趣           |
| POST | `/api/interests/`        | 创建兴趣               |

---

## 🗄️ 数据库设计

### 主要表结构

- `users`: 用户信息（邮箱、是否激活、头像等）
- [interests](file://c:\Users\1\Desktop\ucras\user_management\users\models.py#L8-L8): 兴趣信息（名称、创建时间）
- `user_interests`: 用户与兴趣的关联（排序字段、创建时间）
- `auth_group`, `auth_permission`: 内置权限系统
- `users_user_groups`, `users_user_user_permissions`: 用户与组/权限的多对多关系

---

## 🛠️ 环境配置

在 `settings.py` 中配置：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'user_management',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@qq.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
DEFAULT_FROM_EMAIL = 'your_email@qq.com'

FRONTEND_URL = 'http://127.0.0.1:8000/api/activate'
```

---

## 📦 使用说明

### 安装依赖

```bash
pip install -r requirements.txt
```

### 初始化数据库

```bash
python manage.py migrate
```

### 启动开发服务器

```bash
python manage.py runserver
```

---

## 🖼️ 截图示例

- 注册流程截图：
  - ![注册-格式错误.png](注册-格式错误.png)
  - ![注册-发送激活码.jpg](注册-发送激活码.jpg)
- 登录流程截图：
  - ![登录-token加密.png](登录-token加密.png)
- 兴趣管理截图：
  - ![显示兴趣-阈值10-随机.png](显示兴趣-阈值10-随机.png)
  - ![更新兴趣.png](更新兴趣.png)

---

## 📁 项目目录结构

```
.
├── user_management/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   └── backends.py
├── media/
│   └── avatars/
├── database.sql
├── manage.py
├── requirements.txt
└── outline.txt
```

---

## 📝 备注

- 用户模型继承自 `AbstractUser`，使用邮箱作为唯一标识。
- 使用 `JWT` 进行身份验证。
- 使用 `SMTP` 发送激活邮件并验证邮箱是否存在。
