from web3 import Web3
from ape_tokens import resolve, Amount
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class AaveError(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        super().__init__(message)

class AaveLibrary:
    def __init__(self, network, aave_contract_address):
        self.network = network
        self.web3 = Web3(Web3.HTTPProvider(network))
        self.aave_contract = self.web3.eth.contract(address=aave_contract_address, abi=AAVE_ABI)

    def _resolve_token_address(self, token_symbol):
        return resolve(token_symbol, network=self.network)

    def _calculate_token_amount(self, amount, token_symbol):
        return Amount(f"{amount} {token_symbol}")

    def lend(self, user, amount, token_symbol):
        try:
            token_address = self._resolve_token_address(token_symbol)
            token_amount = self._calculate_token_amount(amount, token_symbol)

            # lending operation using self.aave_contract and token_address
            # ...

            return "Lending successful"
        except Exception as e:
            raise AaveError(f"Lending failed due to error: {str(e)}", code=1001)

    def borrow(self, user, amount, token_symbol):
        try:
            token_address = self._resolve_token_address(token_symbol)
            token_amount = self._calculate_token_amount(amount, token_symbol)

            # borrowing operation using self.aave_contract and token_address
            # ...

            return "Borrowing successful"
        except Exception as e:
            raise AaveError(f"Borrowing failed due to error: {str(e)}", code=1002)

class OperationBundle:
    def __init__(self):
        self.operations = []

    def add_operation(self, operation):
        self.operations.append(operation)

    def exec_all(self):
        results = []
        for operation in self.operations:
            result = operation()
            results.append(result)
        return results

aave_library = AaveLibrary(network="network-url", aave_contract_address="-aave-contract-address")

class MethodRequest(BaseModel):
    user: str
    amount: float
    token_symbol: str

@app.post("/lend")
def lend(request: MethodRequest):
    try:
        result = aave_library.lend(request.user, request.amount, request.token_symbol)
        return {"message": result}
    except AaveError as e:
        raise HTTPException(status_code=400, detail=e.message, headers={"X-Error-Code": str(e.code)})

@app.post("/borrow")
def borrow(request: MethodRequest):
    try:
        result = aave_library.borrow(request.user, request.amount, request.token_symbol)
        return {"message": result}
    except AaveError as e:
        raise HTTPException(status_code=400, detail=e.message, headers={"X-Error-Code": str(e.code)})

@app.post("/exec_all")
def exec_all(methods: List[str]):
    bundle = OperationBundle()
    for method in methods:
        if method == "lend":
            bundle.add_operation(lambda: aave_library.lend("user", 100, "DAI"))
        elif method == "borrow":
            bundle.add_operation(lambda: aave_library.borrow("user", 100, "DAI"))
        # other methods

    results = bundle.exec_all()
    return {"results": results}
