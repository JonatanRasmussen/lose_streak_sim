import random

# CONFIG
BELL_CURVE_MODE = True
GLOBAL_IMPACT_MODIFIER = 0
YOU_ARE_SMURF = True
SMURF_SKILL_MODIFIER = -0.5


class Player:
    MEAN = 0
    STD_DEV = 1

    def __init__(self, skill = 0, base_impact = 1, is_you = False):
        self.skill = skill
        self.base_impact = base_impact
        self.is_you = is_you
        self.randomized_score = self.calculate_randomized_score()
        self.skill_adjusted_score = self.calculate_skill_adjusted_score()
        self.total_impact = self.calculate_total_impact()
        self.final_score = self.calculate_final_score()
        self.team = None

    def calculate_randomized_score(self):
        if BELL_CURVE_MODE:
            contribution = random.gauss(self.MEAN, self.STD_DEV)
        else:
            contribution = random.randint(-50,50)
        return contribution

    def calculate_skill_adjusted_score(self):
        return self.skill + self.randomized_score

    def calculate_total_impact(self):
        extra_impact = abs(self.randomized_score / self.STD_DEV) * GLOBAL_IMPACT_MODIFIER
        return self.base_impact + extra_impact

    def calculate_final_score(self):
        return self.skill_adjusted_score * self.total_impact

    def assign_team(self, team):
        self.team = team

    def promote_to_smurf(self):
        self.skill += self.STD_DEV * SMURF_SKILL_MODIFIER
        self.randomized_score = self.calculate_randomized_score()
        self.skill_adjusted_score = self.calculate_skill_adjusted_score()
        self.total_impact = self.calculate_total_impact()
        self.final_score = self.calculate_final_score()
        if self.team is not None:
            self.team.team_score = self.team.calculate_team_score()


class Team:
    def __init__(self, top=None, jng=None, mid=None, bot=None, supp=None):
        self.top = top if top is not None else Player()
        self.jng = jng if jng is not None else Player()
        self.mid = mid if mid is not None else Player()
        self.bot = bot if bot is not None else Player()
        self.supp = supp if supp is not None else Player()
        self.player_list = [self.top, self.jng, self.mid, self.bot, self.supp]
        self.team_score = self.calculate_team_score()

    def calculate_average_impact(self):
        sum_of_impacts = 0
        for player in self.player_list:
            sum_of_impacts += player.total_impact
        return sum_of_impacts

    def calculate_team_score(self):
        sum_of_final_scores = 0
        for player in self.player_list:
            player.assign_team(self)
            sum_of_final_scores += player.final_score
        return sum_of_final_scores / self.calculate_average_impact()


class Game:
    def __init__(self, your_team=None, enemy_team=None):
        if your_team is None:
            your_team = Team()
        if enemy_team is None:
            enemy_team = Team()
        self.your_team = your_team
        self.enemy_team = enemy_team
        self.all_players = your_team.player_list + enemy_team.player_list
        self.you = self.find_you()
        self.promote_random_smurfs(10)
        self.team_gap = self.your_team.team_score - self.enemy_team.team_score
        self.your_team_won = self.team_gap >= 0
        self.personal_gap = self.gap_to_avg_score()
        self.you_outscored_avg = self.personal_gap >= 0

    def promote_random_smurfs(self, smurf_frequency):
        for player in self.all_players:
            num = random.randint(0,smurf_frequency-1)
            if (num == 0) and (player.skill == 0):
                player.promote_to_smurf()


    def find_you(self):
        for player in self.all_players:
            if player.is_you:
                return player
        new_you = self.your_team.mid
        new_you.is_you = True
        if YOU_ARE_SMURF:
            new_you.promote_to_smurf()
        return new_you

    def gap_to_avg_score(self):
        sorted_players = sorted(self.all_players, key=lambda x: x.skill_adjusted_score, reverse=True)
        top_6_scores = [player.skill_adjusted_score for player in sorted_players[:6]]
        avg_score = (top_6_scores[4] + top_6_scores[5]) / 2
        return self.you.skill_adjusted_score - avg_score


def sim(n):
    deserved_win_tracker = 0
    undeserved_win_tracker = 0
    deserved_loss_tracker = 0
    undeserved_loss_tracker = 0
    other = 0
    for _ in range (0, n):
        game = Game()
        if game.your_team_won and game.you_outscored_avg:
            deserved_win_tracker += 1
        elif game.your_team_won and not game.you_outscored_avg:
            undeserved_win_tracker += 1
        elif not game.your_team_won and not game.you_outscored_avg:
            deserved_loss_tracker += 1
        elif not game.your_team_won and game.you_outscored_avg:
            undeserved_loss_tracker += 1
        else:
            other += 0
    print(f"deserved_wins: {100*deserved_win_tracker/n} %")
    print(f"undeserved_wins: {100*undeserved_win_tracker/n} %")
    print(f"deserved_loss: {100*deserved_loss_tracker/n} %")
    print(f"undeserved_loss: {100*undeserved_loss_tracker/n} %")
    if other != 0:
        print(f"other: {other}")


sim(100000)