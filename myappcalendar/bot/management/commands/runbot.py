from dataclasses import dataclass
from enum import Enum, unique, auto
from typing import Dict

from django.core.management.base import BaseCommand
import os, dotenv
# from myappcalendar.settings import BASE_DIR
# dotenv.load_dotenv(f'{BASE_DIR}/.env')

host = os.environ.get('DOMEN', 'None')


from bot.models import TgUser
from bot.tg.client import TgClient
from goals.models import Goal, GoalCategory


@dataclass
class NewGoal:
    goal_title: str = None
    cat_id: int = 0

    def complete(self) -> bool:
        return None not in {self.cat_id, self.goal_title}


@unique
class StateEnum(Enum):
    CREATE_CATEGORY_STATE = auto()
    CHOSEN_CATEGORY = auto()


@dataclass
class FSM_DATA:
    state: StateEnum
    goals: NewGoal


FSM_STATES: Dict[int, FSM_DATA] = {}


class Command(BaseCommand):
    help = "runbot command"
    tg_client = TgClient(os.environ.get('TOKEN_BOT'))

    @property
    def _generate_code(self) -> str:
        return os.urandom(12).hex()

    def verification_code(self, tg_chat_id, tg_user):
        code = self._generate_code
        tg_user.verification_code = code
        tg_user.save(update_fields=['verification_code'])
        self.tg_client.send_message(
            chat_id=tg_chat_id,
            text=f'verification_code is {code}'
        )

    def select_category(self, message, tg_user: TgUser):
        if message.text.isdigit():
            cat_id = int(message.text)
            if GoalCategory.objects.select_related('user').filter(
                    board__participants__user_id=tg_user.user,
                    is_deleted=False,
                    id=cat_id
            ).exists():
                FSM_STATES[tg_user.telegram_chat_id].goals.cat_id = cat_id
                self.tg_client.send_message(chat_id=message.chat.id, text='Set goal title')
                FSM_STATES[tg_user.telegram_chat_id].state = StateEnum.CHOSEN_CATEGORY
                return
            self.tg_client.send_message(chat_id=message.chat.id, text='invalid category')

    def new_goal(self, message, tg_user: TgUser):
        goal: NewGoal = FSM_STATES[tg_user.telegram_chat_id].goals
        goal.goal_title = message.text
        if goal.complete():
            goal_create = Goal.objects.create(
                title=goal.goal_title,
                category_id=goal.cat_id,
                user=tg_user.user,
                description='Tg goal'
            )
            self.tg_client.send_message(chat_id=message.chat.id,
                                        text=f'http://{host}/categories/goals?goal={goal_create.pk}')
        else:
            self.tg_client.send_message(chat_id=message.chat.id, text=f'Something went wrong!')

    def tg_goal_list(self, message, tg_user: TgUser):
        # TODO Разобраться с %23
        goal_list = [
            f'%23{item.id}{item.title}'.replace(" ", "")
            for item in Goal.objects.filter(user_id=tg_user.user)
        ]
        self.tg_client.send_message(chat_id=message.chat.id, text='\n'.join(goal_list) or ['no goals'])

    def tg_cat_list(self, message, tg_user: TgUser):
        cat_list = [
            f'%23{item.id}{item.title}'
            for item in GoalCategory.objects.select_related('user').filter(
                board__participants__user_id=tg_user.user,
                is_deleted=False
            )
        ]
        if cat_list:
            cat_list_str = '\n'.join(cat_list)
            self.tg_client.send_message(chat_id=message.chat.id, text=f'Select category:\n{cat_list_str}')
        else:
            self.tg_client.send_message(chat_id=message.chat.id, text=f'Categories are not found')

        FSM_STATES.pop(tg_user.telegram_chat_id, None)

    def handle_verified_user(self, message, tg_user: TgUser):
        if message.text == '/goals':
            self.tg_goal_list(message, tg_user)
        elif message.text == '/create':
            self.tg_cat_list(message, tg_user)
            FSM_STATES[tg_user.telegram_chat_id] = FSM_DATA(state=StateEnum.CREATE_CATEGORY_STATE, goals=NewGoal())
            # TODO не совсем верно!
        elif message.text == '/cancel' and tg_user.telegram_chat_id in FSM_STATES:
            FSM_STATES.pop(tg_user.telegram_chat_id)
        elif tg_user.telegram_chat_id in FSM_STATES:
            state: StateEnum = FSM_STATES[tg_user.telegram_chat_id].state
            if state == StateEnum.CREATE_CATEGORY_STATE:
                self.select_category(message=message, tg_user=tg_user)
            elif state == StateEnum.CHOSEN_CATEGORY:
                self.new_goal(message=message, tg_user=tg_user)
        elif not message.text.startswith("/"):
            self.tg_client.send_message(text='Unknown command!', chat_id=message.chat.id)

    def handle(self, *args, **options):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                # user_id = item.message.from_.id
                message = item.message
                tg_chat_id = message.chat.id
                tg_message_id = message.message_id
                tg_username = message.from_.username
                # TgUser_exists = TgUser.objects.filter(telegram_chat_id=tg_chat_id).exists()
                tg_user, created = TgUser.objects.get_or_create(
                    telegram_chat_id=tg_chat_id,
                    defaults={
                        'username': tg_username,
                        'telegram_chat_id': tg_chat_id
                    }
                )
                if created:
                    self.tg_client.send_message(chat_id=tg_chat_id, text='Приветствую друг!')
                    self.verification_code(tg_chat_id=tg_chat_id, tg_user=tg_user)
                elif not tg_user.user:
                    self.verification_code(tg_chat_id=tg_chat_id, tg_user=tg_user)
                elif tg_user.user:
                    self.handle_verified_user(tg_user=tg_user, message=message)
                    # self.tg_client.send_message(chat_id=tg_chat_id, text=f'Пообщаемся {tg_username}!!!')
                    # self.tg_client.send_dice(chat_id=tg_chat_id, emoji='🎯', message_id=tg_message_id)
