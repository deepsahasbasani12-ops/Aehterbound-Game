import random

class Monster:
    def __init__(self, name, hp, mp, atk, type, status=None):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.atk = atk
        self.type = type
        self.status = status or {}

    def is_alive(self):
        return self.hp > 0

    def to_dict(self):
        return {
            "name": self.name,
            "hp": self.hp,
            "mp": self.mp,
            "atk": self.atk,
            "type": self.type,
            "status": self.status,
        }


class Player:
    def __init__(self, name, hp, mp, atk, spells=None, spell=None, status=None):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.atk = atk
        self.spells = spells or []
        self.spell = spell
        self.status = status or {}

    def is_alive(self):
        return self.hp > 0

    def to_dict(self):
        return {
            "name": self.name,
            "hp": self.hp,
            "mp": self.mp,
            "atk": self.atk,
            "spells": self.spells,
            "spell": self.spell,
            "status": self.status,
        }


def battle(player, monster, logs):
    logs.append(f"Fighting {monster.name}!")
    turn = 0
    while player.is_alive() and monster.is_alive():
        turn += 1
        logs.append(f"Turn {turn}:")
        stealth_used = False
        # Player action
        if player.spell and player.spell in SPELLS and player.mp >= SPELLS[player.spell]["cost"]:
            spell_data = SPELLS[player.spell]
            player.mp -= spell_data["cost"]
            logs.append(f"{player.name} uses {player.spell} (costs {spell_data['cost']} MP)!")
            if player.spell == "hp potion":
                heal = spell_data["heal"]
                player.hp += heal
                logs.append(f"{player.name} heals for {heal} HP. {player.name} has {player.hp} HP left.")
            elif player.spell == "mp potion":
                mp_heal = spell_data["heal"]
                player.mp += mp_heal
                logs.append(f"{player.name} restores {mp_heal} MP. {player.name} has {player.mp} MP left.")
            elif player.spell == "stealth":
                stealth_used = True
                damage = player.atk
                monster.hp -= damage
                logs.append(f"{player.name} deals {damage} damage. {monster.name} has {max(0, monster.hp)} HP left.")
                logs.append(f"{player.name} enters stealth mode!")
        else:
            damage = player.atk
            monster.hp -= damage
            logs.append(f"{player.name} attacks {monster.name} for {damage} damage. {monster.name} has {max(0, monster.hp)} HP left.")
        
        if not monster.is_alive():
            logs.append(f"{monster.name} defeated!")
            break
        
        # Monster attacks
        if stealth_used and monster.type != "Boss":
            logs.append(f"{monster.name} can't find {player.name} due to stealth!")
        else:
            mdamage = monster.atk
            player.hp -= mdamage
            logs.append(f"{monster.name} attacks {player.name} for {mdamage} damage. {player.name} has {max(0, player.hp)} HP left.")
        
        if not player.is_alive():
            logs.append(f"{player.name} defeated!")
            break
    return turn


SPELLS = {
    "hp potion": {"cost": 0, "type": "heal", "heal": 3},
    "mp potion": {"cost": 0, "type": "mana", "heal": 10},
    "stealth": {"cost": 10, "type": "defense"},
    "brisingr": {"cost": 20, "type": "attack"},
    "véddr": {"cost": 10, "type": "attack"},
    "reisa": {"cost": 5, "type": "attack"},
    "letta": {"cost": 10, "type": "defense"},
    "thrysta": {"cost": 20, "type": "attack"},
    "gánga": {"cost": 5, "type": "defense"},
}


def do_player_action(player, monster, action, logs):
    spell_data = SPELLS.get(player.spell) if player.spell else None

    if action == 'attack':
        damage = player.atk
        monster.hp -= damage
        logs.append(f"{player.name} attacks {monster.name} for {damage} damage. {monster.name} has {max(0, monster.hp)} HP left.")
    elif action == 'spell' and spell_data:
        if spell_data["type"] in ["attack", "heal", "mana"]:
            if player.mp >= spell_data["cost"]:
                player.mp -= spell_data["cost"]
                logs.append(f"{player.name} uses {player.spell} (costs {spell_data['cost']} MP)!")
                if player.spell == "hp potion":
                    heal = spell_data["heal"]
                    player.hp += heal
                    logs.append(f"{player.name} heals for {heal} HP. {player.name} has {player.hp} HP left.")
                elif player.spell == "mp potion":
                    mp_heal = spell_data["heal"]
                    player.mp += mp_heal
                    logs.append(f"{player.name} restores {mp_heal} MP. {player.name} has {player.mp} MP left.")
                elif player.spell == "brisingr":
                    damage = max(1, int(player.atk * 0.2))
                    monster.hp -= damage
                    monster.status['burn'] = {"turns": 3, "damage": damage}
                    logs.append(f"{player.name} sets Brisingr, burning {monster.name} for {damage} each turn.")
                    if random.random() < 0.3:
                        monster.status['stunned'] = 1
                        logs.append(f"{monster.name} is stunned by Brisingr!")
                elif player.spell == "véddr":
                    damage = max(1, int(player.atk * 0.2))
                    monster.hp -= damage
                    monster.status['stunned'] = 1
                    logs.append(f"{player.name} deals {damage} damage and stuns {monster.name} with Véddr.")
                elif player.spell == "reisa":
                    damage = max(1, int(player.atk * 0.2))
                    monster.hp -= damage
                    if random.random() < 0.3:
                        monster.status['stunned'] = 1
                        logs.append(f"{monster.name} is stunned by Reisa!")
                    logs.append(f"{player.name} deals {damage} damage with Reisa.")
                elif player.spell == "thrysta":
                    multiplier = 1.2 if random.random() < 0.5 else 0.8
                    damage = max(1, int(player.atk * multiplier))
                    monster.hp -= damage
                    logs.append(f"{player.name} uses Thrysta for {damage} damage.")
            else:
                logs.append(f"Not enough MP for {player.spell}! {player.name} attacks instead.")
                damage = player.atk
                monster.hp -= damage
                logs.append(f"{player.name} attacks {monster.name} for {damage} damage. {monster.name} has {max(0, monster.hp)} HP left.")
        elif spell_data["type"] == "defense":
            logs.append(f"{player.name} prepares {player.spell}; it will activate during the enemy attack phase.")
        else:
            damage = player.atk
            monster.hp -= damage
            logs.append(f"{player.name} attacks {monster.name} for {damage} damage. {monster.name} has {max(0, monster.hp)} HP left.")
    else:
        damage = player.atk
        monster.hp -= damage
        logs.append(f"{player.name} attacks {monster.name} for {damage} damage. {monster.name} has {max(0, monster.hp)} HP left.")

    if monster.status.get('burn') and monster.is_alive():
        burn = monster.status['burn']
        burn_damage = burn['damage']
        monster.hp -= burn_damage
        burn['turns'] -= 1
        logs.append(f"{monster.name} suffers {burn_damage} burn damage from Brisingr. {monster.name} has {max(0, monster.hp)} HP left.")
        if burn['turns'] <= 0:
            del monster.status['burn']

    monster_stunned = monster.status.get('stunned', 0) > 0

    battle_over = False
    if not monster.is_alive():
        logs.append(f"{monster.name} defeated!")
        battle_over = True

    return battle_over, False, monster_stunned


def apply_defense_spell(player, monster, pending_damage, logs):
    spell_data = SPELLS.get(player.spell) if player.spell else None
    if not spell_data or spell_data.get("type") != "defense":
        logs.append(f"{player.name} has no defensive spell ready or cannot use {player.spell} now.")
        return pending_damage

    if player.mp < spell_data["cost"]:
        logs.append(f"Not enough MP for {player.spell}! The attack hits normally.")
        return pending_damage

    player.mp -= spell_data["cost"]
    logs.append(f"{player.name} uses {player.spell} to defend! ({spell_data['cost']} MP)")

    if player.spell == "stealth":
        if monster.type != "Boss":
            logs.append(f"{player.name} avoids the attack with Stealth!")
            return 0
        logs.append(f"{player.name} is in Stealth, but the Boss can still hit normally.")
        return pending_damage
    elif player.spell == "letta":
        if random.random() < 0.3:
            reduced = max(0, int(pending_damage * 0.2))
            logs.append(f"{player.name} deflects most damage with Letta! Damage reduced to {reduced}.")
            return reduced
        logs.append(f"{player.name} fails to deflect the attack with Letta.")
        return pending_damage
    elif player.spell == "gánga":
        if random.random() < 0.4:
            logs.append(f"{player.name} dodges the attack with Gánga!")
            return 0
        logs.append(f"{player.name} fails to dodge the attack with Gánga.")
        return pending_damage

    return pending_damage


def run_raid(player_name, player_hp, player_mp, player_atk, player_spell=None):
    spells = [player_spell] if player_spell else []
    player = Player(player_name, player_hp, player_mp, player_atk, spells=spells, spell=player_spell)
    monsters = [
        Monster("Dust Insect", 8, 0, 2, "Normal"),
        Monster("Dust Insect", 8, 0, 2, "Normal"),
        Monster("Scrap Rat", 7, 0, 3, "Normal"),
        Monster("Scrap Rat", 7, 0, 3, "Normal"),
        Monster("Hollow Sprout", 14, 0, 2, "Normal"),
        Monster("Hollow Sprout", 14, 0, 2, "Normal"),
    ]
    boss = Monster("Worn Golem", 30, 10, 4, "Boss")
    logs = ["Starting the raid!"]
    total_turns = 0

    for monster in monsters:
        turns = battle(player, monster, logs)
        total_turns += turns
        if not player.is_alive():
            logs.append("Game over! You were defeated.")
            return {
                "logs": logs,
                "total_turns": total_turns,
                "player_alive": False,
                "player": player.to_dict(),
            }

    logs.append("Now facing the boss!")
    turns = battle(player, boss, logs)
    total_turns += turns

    if player.is_alive():
        logs.append("Congratulations! You won the raid!")
    else:
        logs.append("Defeated by the boss. Game over!")

    logs.append(f"Total turns in the raid: {total_turns}")
    logs.append(f"Claim rewards!!!!!!!!!!!!!!")
    return {
        "logs": logs,
        "total_turns": total_turns,
        "player_alive": player.is_alive(),
        "player": player.to_dict(),
        "boss": boss.to_dict(),
    }
