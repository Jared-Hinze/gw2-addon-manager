# Built-in Libraries
# N/A

# Third Party Libraries
from hypothesis import settings, HealthCheck, Phase, Verbosity

# Local Libraries
# N/A

# ==============================================================================
# Settings
# ==============================================================================
dev = settings.register_profile(
	"dev",
	max_examples=100,
	derandomize=False,
	database=None,
	verbosity=Verbosity.normal,
	phases=tuple(Phase),
	stateful_step_count=50,
	report_multiple_bugs=True,
	suppress_health_check=(),
	deadline=200,  # milliseconds
	print_blob=True,
	backend="hypothesis",
)

ci = settings.register_profile(
	"ci",
	settings.get_profile("dev"),
	derandomize=True,
	deadline=1000 * 60,  # 1 minute
	suppress_health_check=[HealthCheck.too_slow],
)
