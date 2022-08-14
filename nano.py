import minqlx

SUPPORTED_GAMETYPES = ("ca")
DEFAULT_DAMAGE = 150

class nano(minqlx.Plugin):
    def __init__(self):
        self.add_hook("round_end", self.handle_round_end)
        self.add_command(("nano", "nono"), self.cmd_nano)
        self.add_command("ns", self.cmd_nslap)
        self.add_command("nanodbg", self.cmd_nanodbg)

        self.slap_exists = False
        self.caller = None
        self.vote_counter = 0
        self.baiter = None
        self.damage = DEFAULT_DAMAGE
        self.have_voted = []


    def cmd_nano(self, player, msg, channel):
        gt = self.game.type_short
        if gt not in SUPPORTED_GAMETYPES:
            player.tell("This game mode is not supported")
            return
        
        # self.game.state == "in_progress" and
        if  not self.slap_exists:
            self.caller = player
            # Initiate slap vote
            players = self.teams()
            
            count = 0
            last_player_standing = None
            # Ensure that only last player on team exists
            for p in players[self.caller.team]:
                if count > 1:
                    player.tell("Your team needs to have exactly 1 player left")
                    self.caller = None
                    return

                if p.is_alive:
                    count+=1
                    last_player_standing = p

            self.baiter = last_player_standing
            self.msg(f"Petition to slap {self.baiter}, teammates can type !ns to agree")
            self.slap_exists = True
        
        else:
            self.msg(f"In progress: slap {self.baiter}, teammates can type !ns to agree")


    def cmd_nslap(self, player, msg, channel):
        # Make sure there is a vote in progress
        if not self.slap_exists:
            player.tell("No slap vote in progress")
            return

        if player != self.caller:
            players = self.teams()
            player_count = len(players[self.caller.team])
            votes_required = player_count/2

            if player.team == self.caller.team:
                if player not in self.have_voted:
                    self.have_voted.append(player)
                    self.vote_counter+=1
                    more_votes = votes_required - self.vote_counter
                    if more_votes != 0:
                        self.msg(f"Need {more_votes} more votes to slap {self.baiter}")
                else:
                    player.tell("You have already voted")
                    return
            else:
                player.tell("You are not a member of the team that called the slap vote")
                return

            if self.vote_counter > votes_required:
                # Slaps the player
                self.slap(self.baiter, damage=self.damage)
                self.slap_exists = False
                self.caller = None
                self.vote_counter = 0
                self.baiter = None
                self.damage = DEFAULT_DAMAGE
                self.have_voted = []
        else:
            player.tell("You cannot vote to slap yourself")


    def handle_round_end(self, data):
        self.slap_exists = False
        self.caller = None
        self.vote_counter = 0
        self.baiter = None
        self.damage = DEFAULT_DAMAGE
        self.have_voted = []

    def cmd_nanodbg(self, player, msg, channel):
        self.slap_exists = False
        self.caller = None
        self.vote_counter = 0
        self.baiter = None
        self.damage = DEFAULT_DAMAGE
        self.have_voted = []
        self.msg(f"Resetting slap vote stats!")
