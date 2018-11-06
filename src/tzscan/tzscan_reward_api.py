import random
from math import ceil

import math
import requests

from api.reward_api import RewardApi

api_mirror = random.randint(2, 5)  # 1 is over used and not reliable
MAX_PER_PAGE = 50

nb_delegators_call = 'nb_delegators/{}?cycle={}'
rewards_split_call = 'rewards_split/{}?cycle={}&p={}&number={}'

API = {'MAINNET': {'API_URL': 'http://api{}.tzscan.io/v1/'.format(api_mirror)},
       'ALPHANET': {'API_URL': 'http://alphanet-api.tzscan.io/v1/'},
       'ZERONET': {'API_URL': 'http://zeronet-api.tzscan.io/v1/'}
       }


class TzScanRewardApiImpl(RewardApi):

    def __init__(self, nw, baking_address):
        super(TzScanRewardApiImpl, self).__init__()

        self.api = API[nw['NAME']]
        if self.api is None:
            raise Exception("Unknown network {}".format(nw))

        self.baking_address = baking_address

    def get_nb_delegators(self, cycle):
        resp = requests.get(self.api['API_URL'] + nb_delegators_call.format(self.baking_address, cycle))
        if resp.status_code != 200:
            # This means something went wrong.
            raise Exception('GET /tasks/ {}'.format(resp.status_code))
        root = resp.json()
        return root

    def get_rewards_for_cycle_map(self, cycle):
        #############
        nb_delegators = self.get_nb_delegators(cycle)[0]
        nb_delegators_remaining = nb_delegators

        p = 0
        root = {}
        while nb_delegators_remaining > 0:
            resp = requests.get(self.api['API_URL'] + rewards_split_call.
                                format(self.baking_address, cycle, p, min(MAX_PER_PAGE, nb_delegators_remaining)))

            if resp.status_code != 200:
                # This means something went wrong.
                raise Exception('GET /tasks/ {}'.format(resp.status_code))

            if p == 0:  # keep first result as basis; append 'delegators_balance' from other responses
                root = resp.json()
            else:  # only take 'delegators_balance' list and append to 'delegators_balance' list in root
                root["delegators_balance"].extend(resp.json()["delegators_balance"])

            nb_delegators_remaining = nb_delegators_remaining - MAX_PER_PAGE
            p = p + 1

        return root
