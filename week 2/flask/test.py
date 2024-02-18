from werkzeug.security import generate_password_hash

# List of tuples with user data (id, username, plaintext password, role, major)
users = [
    ('018da752-7415-73cb-a5de-df041e74c509', 'janco', 'jancoPass', 'STUDENT', 'IoT'),
    ('018da752-7415-7dff-b7d1-f0fdfa1f51d2', 'Magnus', 'MagnusPass', 'STUDENT', 'IoT'),
    ('018da752-7415-72ec-b87c-9c23fd1c35be', 'jonas', 'jonasPass', 'STUDENT', 'IoT'),
    ('018da752-7415-71c8-ad23-8a7ace93578a', 'Darryl', 'DarrylPass', 'STUDENT', 'IoT'),
    ('018da752-7415-7722-9cf3-e58ee9dfd7e3', 'waut', 'WautPass', 'STUDENT', 'IoT'),
    ('018da752-7416-7268-b499-2975455737ae', 'Jeroen', 'JeroenTeacherPass', 'TEACHER', 'IoT'),
    ('018da752-7416-7ec4-8b32-a82f1a425208', 'Petia', 'PetiaTeacherPass', 'TEACHER', 'IoT'),
    ('018da752-7416-736a-81e6-db29b8d93b9c', 'Thomas', 'ThomasTeacherPass', 'TEACHER', 'IoT'),
    ('018da752-7416-77a1-b3ea-4061e3763a0a', 'Walter', 'WalterTeacherPass', 'TEACHER', 'IoT'),
    ('018da752-7416-779c-babf-7fab72a72444', 'Jelle', 'JelleTeacherPass', 'TEACHER', 'IoT')
]

# Generating hashed passwords
hashed_users = [(user[0], user[1], generate_password_hash(user[2]), user[3], user[4]) for user in users]

# Printing the results
for user in hashed_users:
    print(f"ID: {user[0]}, Username: {user[1]}, Hashed Password: {user[2]}, Role: {user[3]}, Major: {user[4]}")
