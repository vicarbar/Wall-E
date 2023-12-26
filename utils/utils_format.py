# Prints the cards stats of a team or referee
def get_formatted_cards(cards):
    return(f"Estadísticas de *{cards['entity']}*\nAmarillas PP \U0001F7E8: {cards['app']}\nRojas PP \U0001F7E5: {cards['rpp']}\n*Total PP:* {cards['tpp']}")

# Prints the team stats
def get_formatted_team(team):
    return get_formatted_cards(team)

# Prints the cards predictor model results
def get_formatted_card_predictor_probabilities(model_results):
    prob_combinada = model_results['prediccion']
    mensaje = f"*Predicción del modelo: {prob_combinada:.2f}*\n"
    prob_acumulada = 1.0  # Iniciar con probabilidad total

    for num_tarjetas, prob in enumerate(model_results['probabilidades']):
        # Calcula la probabilidad acumulada de más de num_tarjetas
        prob_mas_de = prob_acumulada
        prob_acumulada -= prob
        
        # Formato de mensaje: "+0.5 tarjetas: 98%"
        mensaje += f"+{num_tarjetas + 0.5} tarjetas: {prob_mas_de:.2%}\n"

    return mensaje

# Prints the cards prdictor teams, referee and probabilities
def get_formatted_card_predictor(local_team, visitor_team, referee, model_results):
    return get_formatted_cards(local_team) + "\n\n" + get_formatted_cards(visitor_team) + "\n\n" + get_formatted_cards(referee) + "\n\n" + get_formatted_card_predictor_probabilities(model_results)