# yaback
Yandex backend school intro test

REST API сервис согласно спецификации TASK.pdf

**Инструкция по установке (на примере Ubuntu)**

1. Установите Docker: https://docs.docker.com/install/linux/docker-ce/ubuntu/.
2. Разрешите использование Docker не-root пользователям. Настройте Docker на автозапуск: https://docs.docker.com/install/linux/linux-postinstall/.
3. Установите Docker Compose: https://docs.docker.com/compose/install/.
4. Установите make: ```sudo apt install make```.
5. В корневой директории проекта выполните команду: ```make setup```.

Последняя команда установит необходимые Docker-контейнеры и запустит сервис на http://0.0.0.0:8080, затем прогонит набор тестов.

Чтобы проверить работоспособоность сервиса, можно выполнить команду:
```
curl http://0.0.0.0:8080/dbcheck
```

Эта команда должна возвращать: 
```
{
  "success": true
}
```
