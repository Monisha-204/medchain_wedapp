import hashlib
import json
import time
from datetime import datetime


class Block:
    def __init__(self, index, transactions, previous_hash, miner="Network"):
        self.index = index
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.miner = miner
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "miner": self.miner
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def proof_of_work(self, difficulty=2):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.compute_hash()
        return self.hash

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce,
            "miner": self.miner
        }


class Blockchain:
    DIFFICULTY = 2
    MINING_REWARD = 5.0   # tokens rewarded to miner per block
    INCENTIVE_FEE = 2.0   # tokens charged per operation

    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.wallets = {
            "Network": 1000.0,
            "DiagnosticCenter": 500.0,
            "DoctorClinic": 500.0,
            "Pharmacy": 500.0,
            "LedgerNode": 0.0
        }
        self.patient_records = {}
        self._create_genesis_block()

    # ------------------------------------------------------------------ #
    #  Genesis                                                             #
    # ------------------------------------------------------------------ #
    def _create_genesis_block(self):
        genesis = Block(
            index=0,
            transactions=[{
                "type": "GENESIS",
                "message": "Medical Blockchain Initialized",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }],
            previous_hash="0",
            miner="Network"
        )
        # Mine the genesis block so hash is stable and validation passes
        genesis.proof_of_work(self.DIFFICULTY)
        self.chain.append(genesis)
        print("[BLOCKCHAIN] Genesis block created.")

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #
    @property
    def last_block(self):
        return self.chain[-1]

    def get_patient(self, patient_id):
        return self.patient_records.get(patient_id)

    def _charge_incentive(self, sender, operation):
        """Deduct incentive from sender and credit Network."""
        if self.wallets.get(sender, 0) < self.INCENTIVE_FEE:
            return False, f"{sender} has insufficient balance."
        self.wallets[sender] -= self.INCENTIVE_FEE
        self.wallets["Network"] += self.INCENTIVE_FEE
        tx = {
            "type": "INCENTIVE",
            "from": sender,
            "to": "Network",
            "amount": self.INCENTIVE_FEE,
            "operation": operation,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.pending_transactions.append(tx)
        return True, tx

    def _mine_pending(self, miner="Network"):
        """Mine all pending transactions into a new block."""
        if not self.pending_transactions:
            return None
        # Mining reward
        reward_tx = {
            "type": "MINING_REWARD",
            "to": miner,
            "amount": self.MINING_REWARD,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.wallets[miner] = self.wallets.get(miner, 0) + self.MINING_REWARD
        txs = self.pending_transactions + [reward_tx]
        block = Block(
            index=len(self.chain),
            transactions=txs,
            previous_hash=self.last_block.hash,
            miner=miner
        )
        block.proof_of_work(self.DIFFICULTY)
        self.chain.append(block)
        self.pending_transactions = []
        return block

    # ------------------------------------------------------------------ #
    #  Operations                                                          #
    # ------------------------------------------------------------------ #
    def add_patient_record(self, patient_id, name, age, blood_type, requester):
        ok, result = self._charge_incentive(requester, "ADD_PATIENT")
        if not ok:
            return False, result
        record = {
            "patient_id": patient_id,
            "name": name,
            "age": age,
            "blood_type": blood_type,
            "symptoms": [],
            "prescriptions": [],
            "test_reports": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.patient_records[patient_id] = record
        tx = {
            "type": "ADD_PATIENT",
            "requester": requester,
            "patient_id": patient_id,
            "data": record,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.pending_transactions.append(tx)
        block = self._mine_pending()
        return True, {"message": "Patient record added.", "block": block.to_dict() if block else None, "incentive_tx": result}

    def add_test_report(self, patient_id, report, requester="DiagnosticCenter"):
        ok, result = self._charge_incentive(requester, "ADD_TEST_REPORT")
        if not ok:
            return False, result
        if patient_id not in self.patient_records:
            return False, "Patient not found."
        entry = {"report": report, "by": requester, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.patient_records[patient_id]["test_reports"].append(entry)
        tx = {
            "type": "ADD_TEST_REPORT",
            "requester": requester,
            "patient_id": patient_id,
            "report": entry,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.pending_transactions.append(tx)
        block = self._mine_pending()
        return True, {"message": "Test report added.", "block": block.to_dict() if block else None, "incentive_tx": result}

    def update_symptoms(self, patient_id, symptoms, requester="DoctorClinic"):
        ok, result = self._charge_incentive(requester, "UPDATE_SYMPTOMS")
        if not ok:
            return False, result
        if patient_id not in self.patient_records:
            return False, "Patient not found."
        entry = {"symptoms": symptoms, "by": requester, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.patient_records[patient_id]["symptoms"].append(entry)
        tx = {
            "type": "UPDATE_SYMPTOMS",
            "requester": requester,
            "patient_id": patient_id,
            "symptoms": entry,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.pending_transactions.append(tx)
        block = self._mine_pending()
        return True, {"message": "Symptoms updated.", "block": block.to_dict() if block else None, "incentive_tx": result}

    def add_prescription(self, patient_id, prescription, requester="DoctorClinic"):
        ok, result = self._charge_incentive(requester, "ADD_PRESCRIPTION")
        if not ok:
            return False, result
        if patient_id not in self.patient_records:
            return False, "Patient not found."
        entry = {"prescription": prescription, "by": requester, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        self.patient_records[patient_id]["prescriptions"].append(entry)
        tx = {
            "type": "ADD_PRESCRIPTION",
            "requester": requester,
            "patient_id": patient_id,
            "prescription": entry,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.pending_transactions.append(tx)
        block = self._mine_pending()
        return True, {"message": "Prescription added.", "block": block.to_dict() if block else None, "incentive_tx": result}

    def get_prescription(self, patient_id, requester="Pharmacy"):
        ok, result = self._charge_incentive(requester, "GET_PRESCRIPTION")
        if not ok:
            return False, result
        if patient_id not in self.patient_records:
            return False, "Patient not found."
        prescriptions = self.patient_records[patient_id]["prescriptions"]
        block = self._mine_pending()
        return True, {
            "prescriptions": prescriptions,
            "block": block.to_dict() if block else None,
            "incentive_tx": result
        }

    # ------------------------------------------------------------------ #
    #  Ledger / chain info                                                 #
    # ------------------------------------------------------------------ #
    def get_chain(self):
        return [b.to_dict() for b in self.chain]

    def get_wallets(self):
        return dict(self.wallets)

    def get_all_transactions(self):
        txs = []
        for block in self.chain:
            for tx in block.transactions:
                tx_copy = dict(tx)
                tx_copy["block_index"] = block.index
                txs.append(tx_copy)
        return txs

    def is_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.hash != curr.compute_hash():
                return False
            if curr.previous_hash != prev.hash:
                return False
        return True
