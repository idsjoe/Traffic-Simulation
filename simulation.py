import random
import time
import threading
import pygame
import sys

# Default signal timings
defaultGreen = {0: 10, 1: 10, 2: 10, 3: 10}
defaultRed = 150
defaultYellow = 5

# Simulation Parameters
noOfSignals = 4
currentGreen = 0
nextGreen = (currentGreen + 1) % noOfSignals
currentYellow = 0

# Vehicle Speeds (Pixels per frame)
speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.5}

# Vehicle Starting Positions
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

# Vehicles in Simulation
vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0},
            'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0},
            'up': {0: [], 1: [], 2: [], 'crossed': 0}}

# Vehicle Types
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Signal Positions
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]

# Stop Lines and Default Stops
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Gaps between Vehicles
stoppingGap = 15
movingGap = 15

# Initialize Pygame
pygame.init()
simulation = pygame.sprite.Group()
lock = threading.Lock()

# Load images once to avoid redundant loading
vehicle_images = {}
for direction in ['right', 'down', 'left', 'up']:
    vehicle_images[direction] = {vtype: pygame.image.load(f"images/{direction}/{vtype}.png") for vtype in speeds.keys()}

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        super().__init__()
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.image = vehicle_images[direction][vehicleClass]

        if self.index > 0 and vehicles[direction][lane][self.index - 1].crossed == 0:
            prev_vehicle = vehicles[direction][lane][self.index - 1]
            self.stop = prev_vehicle.stop - prev_vehicle.image.get_width() - stoppingGap
        else:
            self.stop = defaultStop[direction]

        simulation.add(self)

    def move(self):
        global currentGreen, currentYellow
        if self.crossed == 0 and ((self.direction in ['right', 'down'] and self.x + self.image.get_width() > stopLines[self.direction]) or
                                  (self.direction in ['left', 'up'] and self.x < stopLines[self.direction])):
            self.crossed = 1

        if (self.x <= self.stop or self.crossed or (currentGreen == self.direction_number and currentYellow == 0)) and \
                (self.index == 0 or self.x < vehicles[self.direction][self.lane][self.index - 1].x - movingGap):
            self.x += self.speed if self.direction == 'right' else -self.speed

def initialize():
    global signals
    signals.append(TrafficSignal(0, defaultYellow, defaultGreen[0]))
    for i in range(1, noOfSignals):
        signals.append(TrafficSignal(defaultRed, defaultYellow, defaultGreen[i]))
    threading.Thread(target=traffic_control, daemon=True).start()

def traffic_control():
    global currentGreen, currentYellow, nextGreen
    while True:
        with lock:
            while signals[currentGreen].green > 0:
                updateValues()
                time.sleep(1)

            currentYellow = 1
            time.sleep(defaultYellow)
            currentYellow = 0

            signals[currentGreen].green = defaultGreen[currentGreen]
            signals[currentGreen].yellow = defaultYellow
            signals[currentGreen].red = defaultRed

            currentGreen = nextGreen
            nextGreen = (currentGreen + 1) % noOfSignals
            signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green

def updateValues():
    for i in range(noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1

def generateVehicles():
    while True:
        lane_number = random.randint(1, 2)
        vehicle_type = random.choice(list(vehicleTypes.values()))
        direction_number = random.choices(range(4), weights=[25, 25, 25, 25])[0]
        Vehicle(lane_number, vehicle_type, direction_number, directionNumbers[direction_number])
        time.sleep(1)

class Simulation:
    def __init__(self):
        self.screen = pygame.display.set_mode((1400, 800))
        pygame.display.set_caption("Traffic Simulation")
        self.clock = pygame.time.Clock()
        threading.Thread(target=generateVehicles, daemon=True).start()
        self.run()

    def run(self):
        while True:
            self.screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            for vehicle in simulation:
                self.screen.blit(vehicle.image, (vehicle.x, vehicle.y))
                vehicle.move()
            pygame.display.update()
            self.clock.tick(60)

initialize()
Simulation()
