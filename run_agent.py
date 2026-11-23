
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from agent_harness import main

if __name__ == "__main__":
    main()
