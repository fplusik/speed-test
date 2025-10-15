#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Инструмент проверки скорости интернет-соединения
Измеряет скорость загрузки, выгрузки и пинг с детальной статистикой
"""

import time
import requests
import threading
from statistics import mean, median
import json
from datetime import datetime
import os

class InternetSpeedTest:
    def __init__(self):
        self.test_urls = [
            "https://httpbin.org/bytes/1000000",  # 1MB тестовый файл
            "https://httpbin.org/bytes/5000000",  # 5MB тестовый файл
            "https://httpbin.org/bytes/10000000", # 10MB тестовый файл
        ]
        self.ping_urls = [
            "https://www.google.com",
            "https://www.cloudflare.com",
            "https://www.github.com",
            "https://httpbin.org"
        ]
        self.results_file = "speed_test_history.json"
    
    def ping_test(self, url, timeout=5):
        """
        Тестирует ping (время отклика) для URL
        
        Args:
            url (str): URL для тестирования
            timeout (int): Таймаут в секундах
            
        Returns:
            float: Время отклика в миллисекундах или None при ошибке
        """
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            end_time = time.time()
            return (end_time - start_time) * 1000  # в миллисекундах
        except Exception:
            return None
    
    def download_speed_test(self, url, timeout=30):
        """
        Тестирует скорость загрузки
        
        Args:
            url (str): URL файла для загрузки
            timeout (int): Таймаут в секундах
            
        Returns:
            dict: Результаты теста (скорость в Mbps, размер, время)
        """
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            total_size = 0
            chunk_times = []
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunk_start = time.time()
                    total_size += len(chunk)
                    chunk_times.append(time.time() - chunk_start)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Скорость в мегабитах в секунду
            speed_mbps = (total_size * 8) / (total_time * 1000000)
            
            return {
                'success': True,
                'speed_mbps': speed_mbps,
                'size_bytes': total_size,
                'time_seconds': total_time,
                'size_mb': total_size / (1024 * 1024)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'speed_mbps': 0,
                'size_bytes': 0,
                'time_seconds': 0
            }
    
    def upload_speed_test(self, size_mb=1, timeout=30):
        """
        Тестирует скорость выгрузки отправкой данных на httpbin.org
        
        Args:
            size_mb (int): Размер данных для отправки в МБ
            timeout (int): Таймаут в секундах
            
        Returns:
            dict: Результаты теста скорости выгрузки
        """
        try:
            # Создаем тестовые данные
            test_data = 'x' * (size_mb * 1024 * 1024)  # размер в МБ
            url = "https://httpbin.org/post"
            
            start_time = time.time()
            response = requests.post(
                url, 
                data={'data': test_data}, 
                timeout=timeout
            )
            response.raise_for_status()
            end_time = time.time()
            
            total_time = end_time - start_time
            data_size = len(test_data)
            
            # Скорость в мегабитах в секунду
            speed_mbps = (data_size * 8) / (total_time * 1000000)
            
            return {
                'success': True,
                'speed_mbps': speed_mbps,
                'size_bytes': data_size,
                'time_seconds': total_time,
                'size_mb': size_mb
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'speed_mbps': 0,
                'size_bytes': 0,
                'time_seconds': 0
            }
    
    def comprehensive_ping_test(self):
        """Выполняет комплексный тест пинга для нескольких серверов"""
        print("🏓 Тестирование ping...")
        
        results = {}
        for url in self.ping_urls:
            print(f"   Тестирую {url}...")
            pings = []
            
            for i in range(5):  # 5 попыток для каждого сервера
                ping = self.ping_test(url)
                if ping is not None:
                    pings.append(ping)
                time.sleep(0.5)
            
            if pings:
                results[url] = {
                    'pings': pings,
                    'avg': mean(pings),
                    'min': min(pings),
                    'max': max(pings),
                    'median': median(pings)
                }
            else:
                results[url] = {
                    'error': 'Все попытки неудачны'
                }
        
        return results
    
    def comprehensive_speed_test(self):
        """Выполняет полный тест скорости интернета"""
        print("🚀 ТЕСТ СКОРОСТИ ИНТЕРНЕТА")
        print("=" * 50)
        
        # Тест пинга
        ping_results = self.comprehensive_ping_test()
        
        # Тест скорости загрузки
        print("\n📥 Тестирование скорости загрузки...")
        download_results = []
        
        for url in self.test_urls:
            print(f"   Загружаю тестовый файл...")
            result = self.download_speed_test(url)
            if result['success']:
                download_results.append(result)
                print(f"   ✅ {result['speed_mbps']:.2f} Mbps ({result['size_mb']:.1f} MB)")
            else:
                print(f"   ❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            time.sleep(1)
        
        # Тест скорости выгрузки
        print("\n📤 Тестирование скорости выгрузки...")
        upload_result = self.upload_speed_test(1)  # 1MB тест
        if upload_result['success']:
            print(f"   ✅ {upload_result['speed_mbps']:.2f} Mbps ({upload_result['size_mb']} MB)")
        else:
            print(f"   ❌ Ошибка: {upload_result.get('error', 'Неизвестная ошибка')}")
        
        # Формируем итоговые результаты
        test_result = {
            'timestamp': datetime.now().isoformat(),
            'ping': ping_results,
            'download': download_results,
            'upload': upload_result
        }
        
        # Сохраняем результаты
        self.save_test_result(test_result)
        
        # Показываем результаты
        self.display_results(test_result)
        
        return test_result
    
    def display_results(self, result):
        """Отображает результаты тестирования в красивом формате"""
        print("\n" + "=" * 50)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
        # Результаты пинга
        print("\n🏓 PING (время отклика):")
        print("-" * 30)
        
        valid_pings = []
        for url, data in result['ping'].items():
            if 'avg' in data:
                print(f"{url}:")
                print(f"  📊 Среднее: {data['avg']:.1f} мс")
                print(f"  ⚡ Лучшее: {data['min']:.1f} мс")
                print(f"  🐌 Худшее: {data['max']:.1f} мс")
                valid_pings.append(data['avg'])
            else:
                print(f"{url}: ❌ {data.get('error', 'Ошибка')}")
        
        if valid_pings:
            overall_ping = mean(valid_pings)
            print(f"\n🎯 Общий ping: {overall_ping:.1f} мс")
            
            if overall_ping < 20:
                print("   🟢 Отлично!")
            elif overall_ping < 50:
                print("   🟡 Хорошо")
            elif overall_ping < 100:
                print("   🟠 Приемлемо")
            else:
                print("   🔴 Плохо")
        
        # Результаты скорости загрузки
        print(f"\n📥 СКОРОСТЬ ЗАГРУЗКИ:")
        print("-" * 30)
        
        if result['download']:
            speeds = [r['speed_mbps'] for r in result['download'] if r['success']]
            if speeds:
                avg_download = mean(speeds)
                max_download = max(speeds)
                print(f"📊 Средняя скорость: {avg_download:.2f} Mbps")
                print(f"⚡ Максимальная: {max_download:.2f} Mbps")
                
                if avg_download >= 100:
                    print("   🟢 Очень быстро!")
                elif avg_download >= 25:
                    print("   🟡 Быстро")
                elif avg_download >= 5:
                    print("   🟠 Средне")
                else:
                    print("   🔴 Медленно")
            else:
                print("❌ Не удалось измерить скорость загрузки")
        else:
            print("❌ Тесты загрузки не выполнены")
        
        # Результаты скорости выгрузки
        print(f"\n📤 СКОРОСТЬ ВЫГРУЗКИ:")
        print("-" * 30)
        
        if result['upload']['success']:
            upload_speed = result['upload']['speed_mbps']
            print(f"📊 Скорость выгрузки: {upload_speed:.2f} Mbps")
            
            if upload_speed >= 10:
                print("   🟢 Хорошо!")
            elif upload_speed >= 5:
                print("   🟡 Приемлемо")
            elif upload_speed >= 1:
                print("   🟠 Медленно")
            else:
                print("   🔴 Очень медленно")
        else:
            print(f"❌ Ошибка: {result['upload'].get('error', 'Неизвестная ошибка')}")
    
    def save_test_result(self, result):
        """Сохраняет результат теста в файл"""
        try:
            history = []
            if os.path.exists(self.results_file):
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            history.append(result)
            
            # Сохраняем только последние 50 результатов
            if len(history) > 50:
                history = history[-50:]
            
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Ошибка при сохранении результатов: {e}")
    
    def show_history(self, limit=10):
        """Показывает историю тестов"""
        try:
            if not os.path.exists(self.results_file):
                print("История тестов пуста.")
                return
            
            with open(self.results_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if not history:
                print("История тестов пуста.")
                return
            
            print(f"\n📈 ИСТОРИЯ ТЕСТОВ (последние {min(limit, len(history))})")
            print("=" * 60)
            
            for i, test in enumerate(history[-limit:], 1):
                timestamp = datetime.fromisoformat(test['timestamp']).strftime('%Y-%m-%d %H:%M')
                
                # Средний пинг
                ping_values = []
                for url_data in test['ping'].values():
                    if 'avg' in url_data:
                        ping_values.append(url_data['avg'])
                avg_ping = mean(ping_values) if ping_values else 0
                
                # Средняя скорость загрузки
                download_speeds = [r['speed_mbps'] for r in test['download'] if r['success']]
                avg_download = mean(download_speeds) if download_speeds else 0
                
                # Скорость выгрузки
                upload_speed = test['upload']['speed_mbps'] if test['upload']['success'] else 0
                
                print(f"{i}. {timestamp}")
                print(f"   🏓 Ping: {avg_ping:.1f} мс")
                print(f"   📥 Загрузка: {avg_download:.1f} Mbps")
                print(f"   📤 Выгрузка: {upload_speed:.1f} Mbps")
                print()
                
        except Exception as e:
            print(f"Ошибка при чтении истории: {e}")

def main():
    speed_test = InternetSpeedTest()
    
    print("=== ТЕСТ СКОРОСТИ ИНТЕРНЕТА ===\n")
    
    while True:
        print("1. Запустить полный тест скорости")
        print("2. Быстрый тест пинга")
        print("3. Только тест загрузки")
        print("4. Только тест выгрузки")
        print("5. История тестов")
        print("6. Выход")
        
        choice = input("\nВыберите действие (1-6): ")
        
        if choice == "1":
            print("\n🚀 Запуск полного теста...")
            print("⚠️  Это может занять несколько минут и использовать трафик!")
            confirm = input("Продолжить? (y/N): ")
            
            if confirm.lower() == 'y':
                speed_test.comprehensive_speed_test()
            else:
                print("Тест отменен")
                
        elif choice == "2":
            results = speed_test.comprehensive_ping_test()
            valid_pings = []
            
            print("\n🏓 Результаты ping:")
            for url, data in results.items():
                if 'avg' in data:
                    print(f"{url}: {data['avg']:.1f} мс")
                    valid_pings.append(data['avg'])
                else:
                    print(f"{url}: ❌ Ошибка")
            
            if valid_pings:
                print(f"\n🎯 Средний ping: {mean(valid_pings):.1f} мс")
                
        elif choice == "3":
            print("\n📥 Тест скорости загрузки...")
            url = speed_test.test_urls[1]  # Средний размер файла
            result = speed_test.download_speed_test(url)
            
            if result['success']:
                print(f"✅ Скорость загрузки: {result['speed_mbps']:.2f} Mbps")
                print(f"   Загружено: {result['size_mb']:.1f} MB за {result['time_seconds']:.1f} сек")
            else:
                print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
                
        elif choice == "4":
            print("\n📤 Тест скорости выгрузки...")
            result = speed_test.upload_speed_test(0.5)  # 0.5 MB тест
            
            if result['success']:
                print(f"✅ Скорость выгрузки: {result['speed_mbps']:.2f} Mbps")
                print(f"   Отправлено: {result['size_mb']} MB за {result['time_seconds']:.1f} сек")
            else:
                print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
                
        elif choice == "5":
            try:
                limit = int(input("Сколько последних тестов показать? (по умолчанию 10): ") or "10")
                speed_test.show_history(limit)
            except ValueError:
                print("Ошибка: введите корректное число")
                
        elif choice == "6":
            print("До свидания! 🌐")
            break
            
        else:
            print("❌ Неверный выбор. Попробуйте снова.")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
