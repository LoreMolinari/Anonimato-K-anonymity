import argparse
from main import main
import timeit
from utils.data_loader_bank import default_data_configB
from utils.data_loader import default_data_config
import matplotlib.pyplot as plt
import numpy as np
import random


# Configurazione degli argomenti della riga di comando
parser = argparse.ArgumentParser()
parser.add_argument("--samarati", action='store_true', help="Seleziona l'algoritmo Samarati")
parser.add_argument("--mondrian", action='store_true', help="Seleziona l'algoritmo Mondrian")
parser.add_argument("--bank", action='store_true', help="Utilizzare database bank")
args = parser.parse_args()

# k_s = list(range(10, 200, 20)) + list(range(200, 500, 50))

# Parametri per i test completi
k_s_full = list(range(3, 200, 20)) + list(range(200, 350, 30))
maxsup_full = [0, 10, 20, 50, 80, 100, 150, 200, 300]

# Parametri per i test snelliti
# k_s = list(range(10, 200, 20)) + list(range(200, 350, 30))
# maxsup = [0, 50, 100, 200, 300]

# Campionamento dei parametri
# k_s = random.sample(k_s_full, 5)  # Seleziona 5 valori di k
# maxsup = random.sample(maxsup_full, 5)  # Seleziona 5 valori di maxsup

k_s = k_s_full
maxsup = maxsup_full

config = {
    'k': 10, 
    'maxsup': 20, 
    'samarati': False, 
    'mondrian': False,
    'bank': False
    
}
if args.bank:
    config['data'] = default_data_configB
    config['bank'] = True
    
    if args.samarati:
        samarati_elapsed_time = {k: [] for k in maxsup}
        samarati_lm_s = {k: [] for k in maxsup}

        for sup in maxsup:
            for k in k_s:
                config['k'] = k
                config['maxsup'] = sup
                config['samarati'] = True
                # tempo di esecuzione e metrica per ogni esecuzione degli algoritmi
                start = timeit.default_timer()
                lm = main(config)
                samarati_lm_s[sup].append(lm)
                stop = timeit.default_timer()
                samarati_elapsed_time[sup].append(stop - start)

        plt.figure()
        plt.xlabel('k')
        plt.ylabel('runtime (s)')
        plt.title('Samarati runtime')
        for sup in maxsup:
            plt.plot(k_s, samarati_elapsed_time[sup], label='maxsup='+str(sup))
        plt.legend()
        plt.savefig('figs/samarati_runtime_bank.png')
        plt.show()

        plt.figure()
        plt.xlabel('k')
        plt.ylabel('Samarati loss metric')
        plt.title('Samarati loss metric')
        for sup in maxsup:
            plt.plot(k_s, samarati_lm_s[sup], label='maxsup='+str(sup))
        plt.legend()
        plt.savefig('figs/samarati_lm_bank.png')
        plt.show()
        
        print('samarati_elapsed_time:', samarati_elapsed_time)
        print('samarati_lm_s:', samarati_lm_s)


        # print('samarati_elapsed_time:', samarati_elapsed_time)
        # print('samarati_lm_s:', samarati_lm_s)

    elif args.mondrian:
        mondrian_elapsed_time = []
        mondrian_lm_s = []

        for k in k_s:
            config['k'] = k
            config['mondrian'] = True
            # tempo di esecuzione e metrica per ogni esecuzione degli algoritmi
            start = timeit.default_timer()
            lm = main(config)
            mondrian_lm_s.append(lm)
            stop = timeit.default_timer()
            mondrian_elapsed_time.append(stop - start)

        plt.figure()
        plt.xlabel('k')
        plt.ylabel('runtime (s)')
        plt.title('Mondrian runtime')
        plt.plot(k_s, mondrian_elapsed_time)
        plt.legend()
        plt.savefig('figs/mondrian_runtime_bank.png')
        plt.show()

        plt.figure()
        plt.xlabel('k')
        plt.ylabel('loss metric')
        plt.title('Mondrian loss metric')
        plt.plot(k_s, mondrian_lm_s)
        plt.legend()
        plt.savefig('figs/mondrian_lm_bank.png')
        plt.show()

        print('mondrian_elapsed_time:', mondrian_elapsed_time)
        print('mondrian_lm_s:', mondrian_lm_s)

        # print('mondrian_elapsed_time:', mondrian_elapsed_time)
        # print('mondrian_lm_s:', mondrian_lm_s)
    
else:
    config['data'] = default_data_config
    
    if args.samarati:
        samarati_elapsed_time = {k: [] for k in maxsup}
        samarati_lm_s = {k: [] for k in maxsup}

        for sup in maxsup:
            for k in k_s:
                config['k'] = k
                config['maxsup'] = sup
                config['samarati'] = True
                # tempo di esecuzione e metrica per ogni esecuzione degli algoritmi
                start = timeit.default_timer()
                lm = main(config)
                samarati_lm_s[sup].append(lm)
                stop = timeit.default_timer()
                samarati_elapsed_time[sup].append(stop - start)

        plt.figure()
        plt.xlabel('k')
        plt.ylabel('runtime (s)')
        plt.title('Samarati runtime')
        for sup in maxsup:
            plt.plot(k_s, samarati_elapsed_time[sup], label='maxsup='+str(sup))
        plt.legend()
        plt.savefig('figs/samarati_runtime_adult.png')
        plt.show()

        plt.figure()
        plt.xlabel('k')
        plt.ylabel('Samarati loss metric')
        plt.title('Samarati loss metric')
        for sup in maxsup:
            plt.plot(k_s, samarati_lm_s[sup], label='maxsup='+str(sup))
        plt.legend()
        plt.savefig('figs/samarati_lm_adult.png')
        plt.show()
        
        print('samarati_elapsed_time:', samarati_elapsed_time)
        print('samarati_lm_s:', samarati_lm_s)


        # print('samarati_elapsed_time:', samarati_elapsed_time)
        # print('samarati_lm_s:', samarati_lm_s)

    elif args.mondrian:
        mondrian_elapsed_time = []
        mondrian_lm_s = []

        for k in k_s:
            config['k'] = k
            config['mondrian'] = True
            # tempo di esecuzione e metrica per ogni esecuzione degli algoritmi
            start = timeit.default_timer()
            lm = main(config)
            mondrian_lm_s.append(lm)
            stop = timeit.default_timer()
            mondrian_elapsed_time.append(stop - start)

        plt.figure()
        plt.xlabel('k')
        plt.ylabel('runtime (s)')
        plt.title('Mondrian runtime')
        plt.plot(k_s, mondrian_elapsed_time)
        plt.legend()
        plt.savefig('figs/mondrian_runtime_adult.png')
        plt.show()

        plt.figure()
        plt.xlabel('k')
        plt.ylabel('loss metric')
        plt.title('Mondrian loss metric')
        plt.plot(k_s, mondrian_lm_s)
        plt.legend()
        plt.savefig('figs/mondrian_lm_adult.png')
        plt.show()

        print('mondrian_elapsed_time:', mondrian_elapsed_time)
        print('mondrian_lm_s:', mondrian_lm_s)

        # print('mondrian_elapsed_time:', mondrian_elapsed_time)
        # print('mondrian_lm_s:', mondrian_lm_s)

