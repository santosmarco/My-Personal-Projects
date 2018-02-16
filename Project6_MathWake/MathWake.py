from time import sleep, strftime
from random import randint, choice
import pygame
import shelve
import re

pygame.init()

def welcome_message(when=1):
    if when == 0:
        print('---- BEM-VINDO AO MATHWAKE™! ----\n')
    print('''Seus alarmes ativos:
● {}

Comandos:
1:  ADICIONAR UM ALARME
2:  EXCLUIR UM ALARME
3:  IR DORMIR'''.format('\n● '.join(sorted(access_alarms()))))

def access_alarms(mode='r', toWrite={}):
    alarms = shelve.open('alarms')
    if mode == 'r':
        return [x for x in dict(alarms.items()) if alarms[x]]
    elif mode == 'w':
        for key, value in toWrite.items():
            alarms[key] = value
            
def read_command(comm):
    if comm == '1':
        add_alarm()
    elif comm == '2':
        del_alarm()
    elif comm == '3':
        go_sleep()
    else:
        print('\n--- Comando inválido...\n')
        
def add_alarm():
    horaPattern = re.compile(r'([0-1]\d)|(2[0-3])')
    minutosPattern = re.compile(r'([0-5]\d)|\d')
    while True:
        while True:
            hora = input('\n--- Digite a HORA (0-23): ')
            if len(hora) == 1:
                hora = '0'+hora
            if len(horaPattern.findall(hora)) == 1 and len(hora) == 2:
                if len(hora) == 1:
                    hora = '0'+hora
                print(hora, 'e...')
                break
            else:
                print('Hora inválida...')
        while True:
            minutos = input('\n--- Digite os MINUTOS: ')
            if len(minutosPattern.findall(minutos)) == 1:
                if len(minutos) == 1:
                    minutos = '0'+minutos
                print('{}:{}h'.format(hora, minutos))
                break
            else:
                print('Minutos inválidos... ')
        confirm = input('\nCONFIRMA adição de {}:{}h? (S/n) '.format(hora, minutos))
        if confirm == 'S':
            access_alarms('w', {'{}:{}'.format(hora, minutos) : True})
            print('\n--- Horário {}:{}h ADICIONADO!\n'.format(hora, minutos))
        else:
            print()
        break

def del_alarm():
    sAlarms = sorted(access_alarms())
    if len(sAlarms) == 0:
        sAlarms = ['Nenhum alarme']
    whatToDelNegPat = re.compile(r'\D')
    print('\nEsses são os seus alarmes ativos:\n{}'.format(', '.join(sAlarms)))
    if len(sAlarms) > 1:
        while True:
            whatToDel = input('\n--- Digite 1 para excluir o de {}h, 2 p/ {}h, ... : '.format(sAlarms[0], sAlarms[1]))
            if not whatToDelNegPat.search(whatToDel):
                whatToDel = int(whatToDel)
                if whatToDel <= len(sAlarms):
                    break
                else:
                    print('Alarme inválido... ')
            else:
                print('Alarme inválido... ')
    else:
        whatToDel = 1
    if sAlarms != ['Nenhum alarme']:
        confirm = input('\nCONFIRMA exclusão de {}h? (S/n) '.format(sAlarms[whatToDel-1]))
        if confirm == 'S':
            access_alarms('w', {sAlarms[whatToDel-1] : False})
            print('\n--- Horário {}h EXCLUÍDO!\n'.format(sAlarms[whatToDel-1]))
        else:
            print()
    else:
        print('\nNenhum alarme para excluir...\n')
        
def go_sleep():
    print('\n{} alarmes ativados... Me deixe rodando e boa noite!'.format(len(access_alarms())))
    while True:
        sysTime = strftime('%H:%M')
        if sysTime in access_alarms():
            ring()
            print('\nAlarme {} desativado com sucesso.'.format(sysTime))
        sleep(60)

def ring():
    som = pygame.mixer.Sound('alarmsound.wav')
    som.play(loops=-1)
    print('\n---- BOM DIA! ----')
    rights = 0
    while rights < 3:
        q = questions()
        a = input('\n-- Resolva: {}\n'.format(q[0]))
        if a == str(q[1]):
            rights += 1
            print('Acertou! ({}/3)'.format(rights))
        else:
            print('Errou!')
    som.stop()

def questions():
    first = randint(26, 99)
    second = randint(14, 33)
    third = randint(14, 33)
    f_o = choice(['+', 'x'])
    s_o = '+' if f_o == 'x' else 'x'
    result = first+second*third if f_o == '+' else first*second+third
    return ['{} {} {} {} {}'.format(first, f_o, second, s_o, third), result]
    

#Main program:

welcome_message(0)

while True:
    read_command(input())
    sleep(1)
    welcome_message()
