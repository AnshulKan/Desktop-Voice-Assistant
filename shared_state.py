# ==============================================================================
# shared_state.py
# ------------------------------------------------------------------------------
# This module is used to hold global state variables that need to be shared
# and modified across different modules of the application. This is a simple
# way to manage state without passing variables through multiple function calls.
# ==============================================================================

# This flag is used to prevent the main loop in `main.py` from listening for new
# commands while a long-running, background task is active.
#
# For example, when the `set_timer` command in `commands.py` is called, it sets
# this flag to True. The main loop sees this and waits. Once the timer
# countdown is finished, the timer thread sets this flag back to False, and the
# main loop resumes its normal operation.
is_background_task_running = False

