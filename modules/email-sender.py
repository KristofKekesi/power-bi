from modules.custom_logger import CustomLogger

class EmailSender:
	def __init__(self, apiKey: str):
		self.logger = CustomLogger("EmailSender")
		self.apiKey = apiKey
	
	def __call__(self, from_address: str, to_addresses: list[str]):
		# Check from_address and to_addresses via regex
		pass