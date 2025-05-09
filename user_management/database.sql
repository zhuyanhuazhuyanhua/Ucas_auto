CREATE DATABASE IF NOT EXISTS user_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE user_management;

CREATE TABLE IF NOT EXISTS django_content_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    UNIQUE KEY unique_app_model (app_label, model)
);

CREATE TABLE IF NOT EXISTS auth_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS auth_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id),
    UNIQUE KEY unique_content_type_codename (content_type_id, codename)
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined DATETIME NOT NULL,
    avatar VARCHAR(100) NULL
);

CREATE TABLE IF NOT EXISTS interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS user_interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    interest_id INT NOT NULL,
    `order` INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_interest (user_id, interest_id)
);

CREATE TABLE IF NOT EXISTS django_migrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS django_admin_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action_time DATETIME NOT NULL,
    object_id TEXT NULL,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL,
    change_message TEXT NOT NULL,
    content_type_id INT NULL,
    user_id INT NOT NULL,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data LONGTEXT NOT NULL,
    expire_date DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS users_user_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES auth_group(id),
    UNIQUE KEY unique_user_group (user_id, group_id)
);

CREATE TABLE IF NOT EXISTS users_user_user_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permission_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id),
    UNIQUE KEY unique_user_permission (user_id, permission_id)
); 