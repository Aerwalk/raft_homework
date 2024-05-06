import threading
import time
import requests

# Замените адреса и порты на соответствующие вашим узлам
node_urls = [
    "http://127.0.0.1:9030",
    "http://127.0.0.1:9040",
    "http://127.0.0.1:9050",
    "http://127.0.0.1:9020"
]

# Функция для проверки статуса узла
# Функция для проверки статуса узла
def check_node_status(url):
    try:
        response = requests.get(f"{url}/status")
        return response.json()
    except Exception as e:
        print(f"Ошибка при проверке статуса узла {url}: {e}")
        return None

# Тест на чтение данных
def test_read_data():
    for url in node_urls:
        try:
            response = requests.get(f"{url}/get")
            assert response.status_code == 200
            print(f"Значение по адресу {url}: {response.text}")
        except Exception as e:
            print(f"Ошибка при чтении данных с узла {url}: {e}")

# Функция для имитации отказа узла
def simulate_node_failure(url):
    time.sleep(5)  # Имитация времени восстановления узла
    try:
        response = requests.post(f"{url}/sub", data={'value': 5})  # Восстановление узла
        if response.status_code == 200:
            print(f"Узел {url} успешно восстановлен.")
        else:
            print(f"Ошибка при восстановлении узла {url}.")
    except Exception as e:
        print(f"Ошибка при имитации восстановления узла {url}: {e}")

# Тест на отказ узла и восстановление
def test_node_failure_recovery():
    threads = []
    try:
        for url in node_urls:
            thread = threading.Thread(target=simulate_node_failure, args=(url,))
            thread.start()
            threads.append(thread)

        # Добавляем запрос к другому узлу пока один узел недоступен
        backup_url = "http://localhost:9030"  # Замените на адрес резервного узла
        print(f"Выполняем запрос к резервному узлу: {backup_url}")
        response = requests.get(f"{backup_url}/get")
        print(f"Значение с резервного узла: {response.text}")

        # Ждем завершения всех потоков
        for thread in threads:
            thread.join()

        # Проверяем статусы узлов после восстановления
        print("\nСтатусы узлов после восстановления:")
        for url in node_urls:
            status = check_node_status(url)
            if status:
                print(f"Узел {url}: {status}")

        # Делаем запросы к узлам после восстановления
        time.sleep(4)  # Ожидаем восстановления узлов
        print("\nПолученные значения после восстановления:")
        test_read_data()  # Проверяем, что данные можно прочитать после восстановления
    except Exception as e:
        print(f"Ошибка во время теста на отказ и восстановление: {e}")

# Функция для выполнения всех тестов по очереди
def run_all_tests():
    print("Выполнение теста на чтение данных:")
    test_read_data()
    time.sleep(3)  # Пауза перед следующим тестом
    print("\nВыполнение теста на отказ узла и восстановление:")
    test_node_failure_recovery()
# Выполнение всех тестов
run_all_tests()
