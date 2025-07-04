# Built-in Libraries
# N/A

# Third Party Libraries
# N/A

# Local Libraries
# N/A

# ==============================================================================
def has_message(caplog, msg, predicate=str.startswith):
	return any(predicate(m, msg) for m in caplog.messages)
