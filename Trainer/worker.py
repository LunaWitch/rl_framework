import ray
import torch

from user_define.environment import EnvWrapper
from user_define.model import ModelWrapper

from ray import train
class Worker:
    def __init__(self, model_path, user_config, system_config):
        self.model_path = model_path
        self.config = user_config
        self.system = system_config
        self.learning_rate = self.system["TRAIN"]["LEARNING_RATE"]

        self.model = ModelWrapper(self.model_path, self.learning_rate, self.config)
        self.env = EnvWrapper(self.config)

        model_dict = self.model.get_model()
        for k in model_dict:
            model_dict[k].train()

    def ready(self):
        return True

    def preprocess_data(self, state, next_state, action, reward, log_prob, done):
        return self.model.preprocess_data(state, next_state, action, reward, log_prob, done)

    def prepare_model(self):
        model_dict = self.model.get_model()
        for k in model_dict:
            setattr(self, k, train.torch.prepare_model(model_dict[k]))
            
    def train_model(self, batch_state, batch_next_state, batch_action, batch_reward, batch_log_prob, batch_done, batch):
        return self.model.train_model(batch_state, batch_next_state, batch_action, batch_reward, batch_log_prob, batch_done, batch)

    def save_model(self, model_path):
        return self.model.save_model(model_path)
