"""Any strings use for complex logic across components should live in a constant
variable to avoid logical errors caused by typos"""

# number of clumns taken by base stats including normalized quality columns. Does
# not include derived quality columns: bulk, mage, etc.
NUM_STAT_COLUMNS = 14
NUM_STAT_COLUMNS_NO_SPEED = 12
NUM_SPEED_COLUMNS = 2
NUM_QUALITATIVE_COLUMNS = 5


# used for generating column names and processing tables based on col name criteria
GROWTH = "growth"
BASE = "base"
# abbreviated to reduce column emtpy cell space
QUALITY = "qlty"

# These values are tightly coupled to the format of the input data. Keep them here
# to help mitigate the impact on genericness of logic
HP = "HP"
MP = "MP"
PHYSICAL_ATTACK = "WAtk"
PHYSICAL_DEFENSE = "WDef"
MAGIC_ATTACK = "MPow"  # why
MAGIC_DEFENCE = "MRes"  # sillyness but okay
SPEED = "Speed"

BULK_COLUMNS = [HP, HP, PHYSICAL_DEFENSE, MAGIC_DEFENCE]
"""HP is counted twice to give it a higher weight in the result because:
  a. HP is always applicable regardless of attack type
  b. Defense values are cut in half for their respective calculations"""

DAMAGE_COLUMNS = [PHYSICAL_ATTACK, MAGIC_ATTACK]
"""less useful since defense is applicable for all jobs but some jobs use little 
to no magic and vice versa"""

FRONT_LINE_COLUMNS = [HP, PHYSICAL_ATTACK, PHYSICAL_DEFENSE, MAGIC_DEFENCE]
"""Fitness for frontline damage soaking and phsysical attacking"""

MAGE_COLUMNS = [MP, MAGIC_ATTACK]
"""Some mage jobs have rediculously terrible MP growth which necessitates this column"""
