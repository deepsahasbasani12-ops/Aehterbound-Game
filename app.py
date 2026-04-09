from flask import Flask, render_template, request, session, redirect, url_for
import raid_game

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['GET', 'POST'])
def run_raid():
    if request.method == 'GET':
        return redirect(url_for('index'))

    player_name = request.form.get('name', 'Soulflare')
    player_hp = int(request.form.get('hp', 54))
    player_mp = int(request.form.get('mp', 48))
    player_atk = int(request.form.get('atk', 5))
    player_spells = request.form.getlist('spells')
    
    player = raid_game.Player(player_name, player_hp, player_mp, player_atk, spells=player_spells)
    monsters = [
        raid_game.Monster("Dust Insect", 8, 0, 2, "Normal"),
        raid_game.Monster("Dust Insect", 8, 0, 2, "Normal"),
        raid_game.Monster("Scrap Rat", 7, 0, 3, "Normal"),
        raid_game.Monster("Scrap Rat", 7, 0, 3, "Normal"),
        raid_game.Monster("Hollow Sprout", 14, 0, 2, "Normal"),
        raid_game.Monster("Hollow Sprout", 14, 0, 2, "Normal"),
    ]
    boss = raid_game.Monster("Worn Golem", 30, 10, 4, "Boss")
    
    session['player'] = player.to_dict()
    session['monsters'] = [m.to_dict() for m in monsters]
    session['boss'] = boss.to_dict()
    session['current_monster_index'] = 0
    session['logs'] = ["Starting the E Rank Raid!"]
    session['game_over'] = False
    session['phase'] = 'player'
    session['pending_damage'] = 0
    
    return redirect(url_for('battle'))

@app.route('/battle')
def battle():
    if 'player' not in session:
        return redirect(url_for('index'))
    
    player_dict = session['player']
    player = raid_game.Player(**player_dict)
    monsters = [raid_game.Monster(**m) for m in session['monsters']]
    boss = raid_game.Monster(**session['boss'])
    current_index = session['current_monster_index']
    logs = session['logs']
    phase = session.get('phase', 'player')
    
    if current_index < len(monsters):
        current_monster = monsters[current_index]
    elif current_index == len(monsters):
        current_monster = boss
        if not logs or logs[-1] != "Now facing the E Rank Boss!":
            logs.append("Now facing the E Rank Boss!")
            session['logs'] = logs
    else:
        return redirect(url_for('end'))
    
    if session.get('game_over', False):
        return redirect(url_for('end'))
    
    spell_options = player.spells
    defense_spells = [s for s in player.spells if raid_game.SPELLS.get(s, {}).get('type') == 'defense']
    return render_template(
        'battle.html',
        player=player,
        monster=current_monster,
        logs=logs,
        phase=phase,
        spell_options=spell_options,
        defense_spells=defense_spells,
        spell_data=raid_game.SPELLS,
    )

@app.route('/action', methods=['POST'])
def action():
    action = request.form.get('action')
    if action not in ['attack', 'spell', 'skip']:
        action = 'attack'
    
    player_dict = session['player']
    player = raid_game.Player(**player_dict)
    monsters = [raid_game.Monster(**m) for m in session['monsters']]
    boss = raid_game.Monster(**session['boss'])
    current_index = session['current_monster_index']
    logs = session['logs']
    
    if current_index < len(monsters):
        current_monster = monsters[current_index]
    elif current_index == len(monsters):
        current_monster = boss
    else:
        return redirect(url_for('end'))

    phase = session.get('phase', 'player')
    spell_choice = request.form.get('spell_choice')
    if spell_choice and spell_choice not in player.spells:
        spell_choice = None
    player.spell = spell_choice

    if phase == 'player':
        battle_over, _, monster_stunned = raid_game.do_player_action(player, current_monster, action, logs)

        if battle_over:
            if not player.is_alive():
                session['game_over'] = True
                logs.append("Game over! You failed the E Rank Raid.")
            elif current_index < len(monsters):
                session['current_monster_index'] = current_index + 1
            elif current_index == len(monsters):
                logs.append("Congratulations! You completed the E Rank Raid!")
                session['game_over'] = True
            session['phase'] = 'player'
        else:
            if monster_stunned:
                logs.append(f"{current_monster.name} is stunned and cannot attack!")
                current_monster.status['stunned'] -= 1
                if current_monster.status['stunned'] <= 0:
                    del current_monster.status['stunned']
                session['phase'] = 'player'
            else:
                pending_damage = current_monster.atk
                session['pending_damage'] = pending_damage
                session['phase'] = 'defense'
                logs.append(f"{current_monster.name} prepares an attack! Use your defensive spell or skip.")

    elif phase == 'defense':
        pending_damage = session.get('pending_damage', current_monster.atk)
        if action == 'spell' and raid_game.SPELLS.get(player.spell, {}).get('type') == 'defense':
            mdamage = raid_game.apply_defense_spell(player, current_monster, pending_damage, logs)
        else:
            logs.append(f"{player.name} skips defensive action.")
            mdamage = pending_damage

        if mdamage > 0:
            player.hp -= mdamage
            logs.append(f"{current_monster.name} attacks {player.name} for {mdamage} damage. {player.name} has {max(0, player.hp)} HP left.")

        session['pending_damage'] = 0
        session['phase'] = 'player'

        if not player.is_alive():
            session['game_over'] = True
            logs.append("Game over! You failed the E Rank Raid.")

    session['player'] = player.to_dict()
    session['logs'] = logs

    if current_index < len(monsters):
        session['monsters'][current_index] = current_monster.to_dict()
    elif current_index == len(monsters):
        session['boss'] = current_monster.to_dict()

    return redirect(url_for('battle'))

@app.route('/end')
def end():
    logs = session.get('logs', [])
    return render_template('end.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0')
