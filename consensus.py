import argparse
import threading
import time

import requests
from flask import Flask, request, render_template
import logging
class ConsensusManager:
    def __init__(self, init_value: int, my_port: int, other_ports: [int]):
        self.value = init_value
        self.my_port = my_port
        self.other_ports = other_ports
        self.state = "follower"  
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        self.next_index = {port: 1 for port in other_ports}
        self.match_index = {port: 0 for port in other_ports}
        self.election_timeout = 0  # Динамически устанавливаемый таймаут
        self.heartbeat_interval = 0.1  # Подстраиваем под нужды интервал для отправки сердечных импульсов
        self.last_heartbeat_time = 0
        # Дополнительные переменные и код инициализации, специфичные для алгоритма Raft

    def get(self) -> int:
        return self.value
    def start(self):
        # Запуск узла Raft
        threading.Thread(target=self.election_timer).start()

    def election_timer(self):
        while True:
            if self.state == "follower":
                if time.time() - self.last_heartbeat_time > self.election_timeout:
                    self.start_election()
            elif self.state == "leader":
                # Отправка периодических сердечных импульсов для поддержания статуса лидера
                self.send_heartbeats()

            time.sleep(0.1)  # Подстраиваем под нужды интервал ожидания

    def start_election(self):
        self.state = "candidate"
        self.current_term += 1
        self.voted_for = self.my_port
        # Отправка запросов на голосование (RequestVote RPC) всем другим узлам
        # Переход к статусу лидера, если кандидат получает большинство голосов
        # Иначе начать новый таймаут выборов и продолжить процесс

    def add(self, value: int):
        self.log.append(("add", value))
        self.value += value
        return self.value


    def sub(self, value: int):
        self.log.append(("sub", value))
        self.value -= value
        return self.value

    def mul(self, value: int):
        self.log.append(("mul", value))
        self.value *= value
        return self.value

    def get_status(self) -> str:
        return "some_status_for_logging"

    def send_append_entries(self, action, value, destination_port):
        try:
            # Отправка RPC AppendEntries с информацией о действии и значении
            response = requests.post(f"http://localhost:{destination_port}/append_entries",
                                     json={'action': action, 'value': value})
            if response.status_code == 200:
                print(f"RPC AppendEntries успешно отправлен на порт {destination_port}")
            else:
                print(f"Ошибка при отправке RPC AppendEntries на порт {destination_port}: {response.status_code}")
        except Exception as e:
            print(f"Ошибка при отправке RPC AppendEntries на порт {destination_port}: {e}")

    def send_heartbeats(self):
        for port in self.other_ports:
            # Отправка RPC AppendEntries с пустыми записями в качестве сердечных импульсов
            self.send_append_entries(None, None, destination_port=port)
        self.last_heartbeat_time = time.time()  # Обновление времени последнего сердечного импульса