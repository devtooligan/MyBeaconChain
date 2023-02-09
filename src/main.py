import random


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Block:
    def __init__(self, number):
        self.hash = str("0x<somehash{}>".format(number))
        self.transactions = [{"id": 1, "stuff": "abc"}, {"id": 2, "stuff": "def"}]


class Proposal:
    def __init__(self, block):
        self.block = block
        self.justified = False
        self.finalized = False


class Slot:
    def __init__(self, index, epoch):
        self.index = index
        self.epoch = epoch
        self.committee = []

    def propose(self, proposal):
        self.proposal = proposal

    def assign_proposer(self, validator):
        self.proposer = validator

    def assign_committee_member(self, validator):
        self.committee.append(validator)


class Epoch:
    def __init__(self, index):
        self.index = index
        self.offset = self.index * 32
        self.slots = {}
        self._initialize_slots()
        self.checkpoint = None
        self.checkpoint_votes = 0
        self.checkpoint_justified = False
        self.checkpoint_finalized = False

    def _initialize_slots(self):
        for slot in range(self.offset, self.offset + 32):
            self.slots[slot] = Slot(slot, self)


class Validator:
    def __init__(self, id, beaconchain):
        self.id = id
        self.balance = random.randint(16, 32)  # total ETH staked
        self.beaconchain = beaconchain
        beaconchain.register_validator(self)

    def vote_yes(self, slot):
        payload = {
            "LMD GHOST": slot.proposal.block.hash,
            "FFG": slot.epoch.checkpoint,
            "validator_id": self.id,
            "slot": slot.index,
            "current_balance": self.balance,
        }

        self.beaconchain.vote(payload)

    def propose(self, slot, block):
        beaconchain.propose_block(slot, block)


class BeaconChain:
    def __init__(self):
        print()
        print("Creating new Beacon Chain")
        print()
        self.finalized = []
        self.justified = []
        self.attested = []
        self.validators = {}
        self.epochs = {}
        self.votes = {}

    def register_validator(self, validator):
        self.validators[validator.id] = validator

    def new_epoch(self):
        print("█▄░█ █▀▀ █░█░█   █▀▀ █▀█ █▀█ █▀▀ █░█")
        print("█░▀█ ██▄ ▀▄▀▄▀   ██▄ █▀▀ █▄█ █▄▄ █▀█")
        self._initialize_epoch()
        self._assign_proposers()
        self._assign_committees()

        # start processing slots!
        for slot_idx, slot in self.current_epoch.slots.items():
            print()
            self._accept_proposal(slot)
            print("Slot {} block proposed: {}".format(slot_idx, slot.proposal.block.hash))
            self._accept_votes()
            result = self._tally_votes()

            if result:
                self.current_slot.proposal.attested = True
                self.attested.append(self.current_slot.proposal.block.hash)
                print(
                    bcolors.OKGREEN + "Block {} in slot {} attested".format(
                        self.current_slot.proposal.block.hash, self.current_slot.index
                    ) + bcolors.ENDC
                )
                print()
            if self.current_slot.index == self.current_epoch.offset + 31:
                self._end_epoch()
            else:
                self.current_slot = self.current_epoch.slots[
                    self.current_slot.index + 1
                ]

    def _end_epoch(self):
        # This actually could happen before the end of the epoch, but for simplicity
        # we'll just do it at the end of the epoch
        print()
        print("█▀▀ █▀█ █▀█ █▀▀ █░█   █▀▀ █▀█ █▀▄▀█ █▀█ █░░ █▀▀ ▀█▀ █▀▀")
        print("██▄ █▀▀ █▄█ █▄▄ █▀█   █▄▄ █▄█ █░▀░█ █▀▀ █▄▄ ██▄ ░█░ ██▄")
        print("End of epoch {}".format(self.current_epoch.index))

        total_validator_balances = sum([v.balance for v in self.validators.values()])
        pct = 1.0 * self.current_epoch.checkpoint_votes / total_validator_balances
        if pct > 2.0 / 3:
            self.current_epoch.checkpoint_justified = True
            print("Checkpoint {} justified".format(self.current_epoch.checkpoint))
            self.justified.append(self.current_epoch.checkpoint)
            if self.current_epoch.index > 0:
                prev_epoch = self.epochs[self.current_epoch.index - 1]
                if prev_epoch.checkpoint_justified:
                    self._finalize(prev_epoch)

    def _finalize(self, epoch):
        print()
        print("Finalizing checkpoint from epoch {}.".format(epoch.index))

        print(bcolors.OKBLUE + "Block {} FINALIZED".format(epoch.checkpoint) + bcolors.ENDC)
        print()
        epoch.checkpoint_finalized = True
        self.finalized.append(epoch.checkpoint)

    def _initialize_epoch(self):
        if not getattr(self, "current_epoch", None):
            self.current_epoch = Epoch(0)
        else:
            self.current_epoch = Epoch(self.current_epoch.index + 1)
        self.epochs[self.current_epoch.index] = self.current_epoch
        self.current_slot = self.current_epoch.slots[self.current_epoch.offset]
        # initialize votes
        for idx in range(self.current_epoch.offset, self.current_epoch.offset + 32):
            self.votes[idx] = {}

        print("Initializing epoch {}".format(self.current_epoch.index))

    def _assign_proposers(self):
        print()
        print("Assigning proposers for slot randomly weighted by staked amount")
        candidate_ids = []
        for validator in self.validators.values():
            candidate_ids += [
                validator.id
            ] * validator.balance  # give one "vote" per staked ETH

        for slot in range(self.current_slot.index, self.current_slot.index + 32):
            choice = candidate_ids.pop(random.randint(0, len(candidate_ids)))
            print("Validator {} chosen as proposer for slot {}".format(choice, slot))
            self.current_epoch.slots[slot].assign_proposer(self.validators[choice])
            candidate_ids = [
                id for id in candidate_ids if id != choice
            ]  # remove the chosen validator's "votes" from list

    def _assign_committees(self):
        if len(self.validators) < 4096:
            raise Exception("Not enough validators")
        if len(self.validators) > 8191:
            raise Exception("Multiple committees not implemented")
        print()
        print("Assigning committees for slots")
        candidate_ids = [validator.id for validator in self.validators.values()]
        starting_slot_idx = self.current_epoch.offset
        current_slot_idx = starting_slot_idx
        while len(candidate_ids):
            choice = candidate_ids.pop(random.randint(0, len(candidate_ids) - 1))
            self.current_epoch.slots[current_slot_idx].assign_committee_member(
                self.validators[choice]
            )
            current_slot_idx += 1
            if current_slot_idx >= starting_slot_idx + 32:
                current_slot_idx = starting_slot_idx
        print("All validators assigned to a committee")
        for idx, slot in self.current_epoch.slots.items():
            print(
                "Slot {} total committee members: {}".format(idx, len(slot.committee))
            )

    def _accept_proposal(self, slot):
        # Normally these proposals would be broadcast to the network, here we are triggering them manually
        slot.proposer.propose(slot, Block(slot.index))

    def propose_block(self, slot, block):
        # called by proposer
        proposal = Proposal(block)
        slot.propose(proposal)
        if slot.index == self.current_epoch.offset:
            self.current_epoch.checkpoint = proposal.block.hash

    def _accept_votes(self):
        print("Accepting votes...")
        # Normally these votes would be broadcast to the network, here we are triggering them manually
        for attestor in self.current_slot.committee:
            # Simulating a 90% chance of voting yes
            # No vote due to lag, downtime, or other reasons
            # Source: my bum -- I have no idea if that is close to reality!
            if random.randint(1, 100) <= 90:
                attestor.vote_yes(self.current_slot)

    def vote(self, payload):
        # called "attestor", a validator chosen as committe member for this slot
        self.votes[payload["slot"]][payload["validator_id"]] = payload

    def _tally_votes(self):
        print("Tallying votes!")
        committee_members = self.current_slot.committee
        votes_in_favor = 1.0
        for member in committee_members:
            if member.id in self.votes[self.current_slot.index]:
                vote = self.votes[self.current_slot.index][member.id]
                if vote["LMD GHOST"] == self.current_slot.proposal.block.hash:
                    votes_in_favor += vote["current_balance"]
                if vote["FFG"] == self.current_epoch.checkpoint:
                    self.current_epoch.checkpoint_votes += vote["current_balance"]
        total_staked_by_committee = sum(
            [member.balance for member in committee_members]
        )
        pct = votes_in_favor / total_staked_by_committee
        print(
            "{} votes in favor out of {} = {:.0f}%".format(
                votes_in_favor, total_staked_by_committee, 100 * pct
            )
        )
        return pct > (2 / 3.0)


beaconchain = BeaconChain()
validators = []
NUMBER_OF_VALIDATORS = 6000
for idx in range(NUMBER_OF_VALIDATORS):
    new_validator = Validator(idx, beaconchain)
    validators.append(new_validator)

while True:
    beaconchain.new_epoch()
    x = input("Enter to continue on to the next epoch, anything else to quit ")
    print()
    if x:
        break
