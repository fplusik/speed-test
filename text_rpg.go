package main

import (
	"bufio"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"strings"
	"time"
)

// Структуры для игры
type Character struct {
	Name     string
	Health   int
	MaxHealth int
	Attack   int
	Defense  int
	Level    int
	Experience int
	Inventory []string
}

type Monster struct {
	Name    string
	Health  int
	Attack  int
	Defense int
	Reward  int
}

type Room struct {
	Description string
	Exits       map[string]int
	HasMonster  bool
	Monster     *Monster
	HasTreasure bool
	Treasure    string
	Visited     bool
}

// Глобальные переменные
var (
	player Character
	rooms  []Room
	currentRoom int
	gameRunning bool
)

// Инициализация игры
func initGame() {
	player = Character{
		Name:      "Герой",
		Health:    100,
		MaxHealth: 100,
		Attack:    20,
		Defense:   10,
		Level:     1,
		Experience: 0,
		Inventory: []string{"Зелье здоровья", "Хлеб"},
	}

	// Создание комнат
	rooms = []Room{
		{
			Description: "🏛️ Вы находитесь в древнем храме. Каменные колонны поддерживают высокий потолок.",
			Exits:       map[string]int{"север": 1, "восток": 2},
			HasTreasure: true,
			Treasure:    "Старинный ключ",
		},
		{
			Description: "🌲 Темный лес окружает вас. Слышны странные звуки.",
			Exits:       map[string]int{"юг": 0, "север": 3},
			HasMonster:  true,
			Monster: &Monster{
				Name:    "Лесной волк",
				Health:  30,
				Attack:  15,
				Defense: 5,
				Reward:  25,
			},
		},
		{
			Description: "🏰 Заброшенная башня возвышается перед вами.",
			Exits:       map[string]int{"запад": 0, "север": 4},
			HasTreasure: true,
			Treasure:    "Магический свиток",
		},
		{
			Description: "⛰️ Горная пещера. Капли эхом отдаются в темноте.",
			Exits:       map[string]int{"юг": 1},
			HasMonster:  true,
			Monster: &Monster{
				Name:    "Пещерный тролль",
				Health:  50,
				Attack:  25,
				Defense: 8,
				Reward:  50,
			},
		},
		{
			Description: "🏺 Сокровищница! Золото блестит в лучах света.",
			Exits:       map[string]int{"юг": 2},
			HasTreasure: true,
			Treasure:    "Золотой меч (+10 атака)",
		},
	}

	currentRoom = 0
	gameRunning = true
}

// Основной игровой цикл
func main() {
	fmt.Println("🎮 ДОБРО ПОЖАЛОВАТЬ В ТЕКСТОВУЮ RPG!")
	fmt.Println("=====================================")
	fmt.Println()

	rand.Seed(time.Now().UnixNano())
	initGame()

	scanner := bufio.NewScanner(os.Stdin)

	for gameRunning {
		showRoom()
		fmt.Print("\n> ")
		
		if scanner.Scan() {
			command := strings.ToLower(strings.TrimSpace(scanner.Text()))
			processCommand(command)
		}
	}

	fmt.Println("Спасибо за игру! 👋")
}

// Отображение текущей комнаты
func showRoom() {
	room := &rooms[currentRoom]
	
	fmt.Println("\n" + strings.Repeat("=", 50))
	fmt.Println(room.Description)
	
	if !room.Visited {
		room.Visited = true
		player.Experience += 5
		fmt.Println("✨ +5 опыта за исследование!")
	}

	// Показываем выходы
	fmt.Print("🚪 Выходы: ")
	for direction := range room.Exits {
		fmt.Print(direction + " ")
	}
	fmt.Println()

	// Показываем монстра
	if room.HasMonster && room.Monster.Health > 0 {
		fmt.Printf("⚔️  Здесь находится %s (HP: %d)\n", 
			room.Monster.Name, room.Monster.Health)
	}

	// Показываем сокровище
	if room.HasTreasure {
		fmt.Printf("💎 Здесь лежит: %s\n", room.Treasure)
	}

	// Показываем статус игрока
	fmt.Printf("\n👤 %s | HP: %d/%d | Уровень: %d | Опыт: %d\n", 
		player.Name, player.Health, player.MaxHealth, player.Level, player.Experience)
}

// Обработка команд
func processCommand(command string) {
	parts := strings.Split(command, " ")
	action := parts[0]

	switch action {
	case "север", "юг", "восток", "запад":
		move(action)
	case "атака", "бить":
		attack()
	case "взять":
		takeTreasure()
	case "инвентарь", "inv":
		showInventory()
	case "использовать":
		if len(parts) > 1 {
			useItem(strings.Join(parts[1:], " "))
		} else {
			fmt.Println("Использовать что?")
		}
	case "статус":
		showStatus()
	case "помощь", "help":
		showHelp()
	case "выход", "quit":
		gameRunning = false
	default:
		fmt.Println("Не понимаю эту команду. Введите 'помощь' для списка команд.")
	}

	// Проверка уровня
	checkLevelUp()
}

// Движение между комнатами
func move(direction string) {
	room := &rooms[currentRoom]
	
	if nextRoom, exists := room.Exits[direction]; exists {
		// Проверяем, есть ли живой монстр
		if room.HasMonster && room.Monster.Health > 0 {
			fmt.Println("❌ " + room.Monster.Name + " блокирует путь! Вы должны сражаться!")
			return
		}
		
		currentRoom = nextRoom
		fmt.Printf("🚶 Вы идете на %s...\n", direction)
		
		// Случайная встреча
		if rand.Intn(10) < 2 {
			randomEvent()
		}
	} else {
		fmt.Println("❌ Вы не можете пройти в этом направлении.")
	}
}

// Атака монстра
func attack() {
	room := &rooms[currentRoom]
	
	if !room.HasMonster || room.Monster.Health <= 0 {
		fmt.Println("❌ Здесь некого атаковать.")
		return
	}

	monster := room.Monster
	
	// Атака игрока
	damage := player.Attack + rand.Intn(10) - monster.Defense
	if damage < 0 {
		damage = 0
	}
	
	monster.Health -= damage
	fmt.Printf("⚔️  Вы атакуете %s и наносите %d урона!\n", monster.Name, damage)

	if monster.Health <= 0 {
		fmt.Printf("🎉 Вы победили %s!\n", monster.Name)
		player.Experience += monster.Reward
		fmt.Printf("✨ +%d опыта!\n", monster.Reward)
		
		// Случайная добыча
		if rand.Intn(3) == 0 {
			loot := []string{"Зелье здоровья", "Золото", "Зелье силы"}
			item := loot[rand.Intn(len(loot))]
			player.Inventory = append(player.Inventory, item)
			fmt.Printf("💰 Вы нашли: %s\n", item)
		}
		return
	}

	// Атака монстра
	monsterDamage := monster.Attack + rand.Intn(8) - player.Defense
	if monsterDamage < 0 {
		monsterDamage = 0
	}
	
	player.Health -= monsterDamage
	fmt.Printf("💥 %s атакует вас и наносит %d урона!\n", monster.Name, monsterDamage)

	if player.Health <= 0 {
		fmt.Println("💀 Вы погибли! Игра окончена.")
		gameRunning = false
	}
}

// Взять сокровище
func takeTreasure() {
	room := &rooms[currentRoom]
	
	if !room.HasTreasure {
		fmt.Println("❌ Здесь нет ничего ценного.")
		return
	}

	fmt.Printf("✨ Вы взяли: %s\n", room.Treasure)
	
	// Специальные предметы
	if strings.Contains(room.Treasure, "Золотой меч") {
		player.Attack += 10
		fmt.Println("⚔️  Ваша атака увеличилась на 10!")
	}
	
	player.Inventory = append(player.Inventory, room.Treasure)
	room.HasTreasure = false
	room.Treasure = ""
}

// Показать инвентарь
func showInventory() {
	fmt.Println("\n🎒 ИНВЕНТАРЬ:")
	if len(player.Inventory) == 0 {
		fmt.Println("  (пусто)")
		return
	}
	
	for i, item := range player.Inventory {
		fmt.Printf("  %d. %s\n", i+1, item)
	}
}

// Использовать предмет
func useItem(itemName string) {
	for i, item := range player.Inventory {
		if strings.Contains(strings.ToLower(item), strings.ToLower(itemName)) {
			fmt.Printf("🧪 Вы используете: %s\n", item)
			
			switch {
			case strings.Contains(item, "Зелье здоровья"):
				heal := 30
				player.Health += heal
				if player.Health > player.MaxHealth {
					player.Health = player.MaxHealth
				}
				fmt.Printf("💚 Вы восстановили %d здоровья!\n", heal)
				
			case strings.Contains(item, "Зелье силы"):
				player.Attack += 5
				fmt.Println("💪 Ваша сила увеличилась на 5!")
				
			case strings.Contains(item, "Хлеб"):
				player.Health += 10
				if player.Health > player.MaxHealth {
					player.Health = player.MaxHealth
				}
				fmt.Println("🍞 Вы немного подкрепились (+10 HP)")
				
			default:
				fmt.Println("❓ Вы не знаете, как использовать этот предмет.")
				return
			}
			
			// Удаляем использованный предмет
			player.Inventory = append(player.Inventory[:i], player.Inventory[i+1:]...)
			return
		}
	}
	
	fmt.Println("❌ У вас нет такого предмета.")
}

// Показать статус
func showStatus() {
	fmt.Println("\n📊 СТАТУС ПЕРСОНАЖА:")
	fmt.Printf("  Имя: %s\n", player.Name)
	fmt.Printf("  Здоровье: %d/%d\n", player.Health, player.MaxHealth)
	fmt.Printf("  Атака: %d\n", player.Attack)
	fmt.Printf("  Защита: %d\n", player.Defense)
	fmt.Printf("  Уровень: %d\n", player.Level)
	fmt.Printf("  Опыт: %d\n", player.Experience)
	fmt.Printf("  Предметов: %d\n", len(player.Inventory))
}

// Случайные события
func randomEvent() {
	events := []string{
		"Вы нашли немного золота!",
		"Странный торговец предлагает зелье здоровья.",
		"Вы чувствуете магическую энергию в воздухе.",
		"Холодный ветер пробирает до костей.",
		"Вы слышите далекий рев дракона.",
	}
	
	event := events[rand.Intn(len(events))]
	fmt.Printf("🎲 %s\n", event)
	
	if event == events[0] { // Золото
		player.Inventory = append(player.Inventory, "Золото")
	} else if event == events[1] { // Торговец
		player.Inventory = append(player.Inventory, "Зелье здоровья")
	}
}

// Проверка повышения уровня
func checkLevelUp() {
	requiredExp := player.Level * 100
	
	if player.Experience >= requiredExp {
		player.Level++
		player.MaxHealth += 20
		player.Health = player.MaxHealth
		player.Attack += 5
		player.Defense += 2
		player.Experience -= requiredExp
		
		fmt.Printf("\n🎊 ПОВЫШЕНИЕ УРОВНЯ!\n")
		fmt.Printf("🆙 Теперь вы %d уровня!\n", player.Level)
		fmt.Printf("💪 Атака: +5, Защита: +2, Здоровье: +20\n")
	}
}

// Справка
func showHelp() {
	fmt.Println("\n📖 ДОСТУПНЫЕ КОМАНДЫ:")
	fmt.Println("  север/юг/восток/запад - движение")
	fmt.Println("  атака - атаковать монстра")
	fmt.Println("  взять - взять предмет")
	fmt.Println("  инвентарь - показать инвентарь")
	fmt.Println("  использовать [предмет] - использовать предмет")
	fmt.Println("  статус - показать характеристики")
	fmt.Println("  помощь - эта справка")
	fmt.Println("  выход - завершить игру")
}
