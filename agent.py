import torch
import random
from collections import deque
from car import Car
from game_environment_AI import GameEnvironmentAI, Direction
from model import Linear_QNet, QTrainer
from utils import plot

MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001

MAX_CHECKPOINT_DIST = 300

class Agent:
    def __init__(self):
        self.number_of_games = 0
        self.epsilon = 0
        self.gamma = 0.9    # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # when it gets full it pops the element from the left side of the queue
        self.model = Linear_QNet(6, 256, 6)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        

    def get_state(self, game):
        state = [
            round(game.dist_to_checkpoint / MAX_CHECKPOINT_DIST, 3), # normalize
            round(game.car.vel / game.car.max_vel, 3),
            round(game.angle_to_checkpoint, 3),
            int(game.car.danger[0]),
            int(game.car.danger[1]),
            int(game.car.danger[2])
        ]
        return state

    def store_in_memory(self, state, action, reward, next_state, is_step_done):     # store a state as a tuple
        self.memory.append((state, action, reward, next_state, is_step_done))

    def train_long_memory(self):    # train multiple states
        if len(self.memory) < BATCH_SIZE:
            training_sample = self.memory
        else:
            training_sample = random.sample(self.memory, BATCH_SIZE)

        states, actions, rewards, next_states, is_step_dones = zip(*training_sample)    # unpack the training_sample tuples into tuples containing only states, actions, rewards etc.
        self.trainer.train_step(states, actions, rewards, next_states, is_step_dones)

    def train_short_memory(self, state, action, reward, next_state, is_step_done):  # train 1 state
        self.trainer.train_step(state, action, reward, next_state, is_step_done)

    def get_action(self, state):
        self.epsilon = 25 - self.number_of_games
        if random.randint(0, 200) < self.epsilon:
            final_move = random.randint(1, 6)
        else:
            state0 = torch.tensor(state, dtype=torch.float)     # convert the state (numpy array) into a pytorch tensor
            prediction = self.model(state0)
            final_move = torch.argmax(prediction).item() + 1
            # print("final move" , final_move)
        return final_move


def train(car):
    scores = []
    average_scores = []
    total_score = 0
    record_score = 0
    agent = Agent()
    game = GameEnvironmentAI(car)

    while True:
        state_current = agent.get_state(game)
        next_move = agent.get_action(state_current)
        reward, is_step_done, current_score = game.play_step(next_move)
        state_new = agent.get_state(game)
        agent.train_short_memory(state_current, next_move, reward, state_new, is_step_done)
        agent.store_in_memory(state_current, next_move, reward, state_new, is_step_done)

        if is_step_done:
            # train long memory (replay memory/experience replay)
            # plot results
            game.reset()
            agent.number_of_games += 1
            agent.train_long_memory()
            if (current_score > record_score):
                record_score = current_score

            print("Game #", agent.number_of_games, "score: ", current_score, "record: ", record_score)

            scores.append(current_score)
            total_score += current_score
            average_score = total_score / agent.number_of_games
            average_scores.append(average_score)
            plot(scores, average_scores)
                  

if __name__ == '__main__':
    car = Car()
    train(car)