from aiogram.dispatcher.filters.state import StatesGroup, State


class User(StatesGroup):
    untilApproved = State()
    mainMenu = State()


class AdminMenu(StatesGroup):
    adminMenu = State()


class Code_check(StatesGroup):
    Q1 = State()


class PurchaseMono(StatesGroup):
    checkPayment = State()


class Purchase(StatesGroup):
    selectedProduct = State()
    selectQuantity = State()
    purchaseProduct = State()


class RedactProduct(StatesGroup):
    changeRedaction = State()
    getNewName = State()
    getNewDescription = State()
    getNewPrice = State()
    getNewPhoto = State()


class CreateProduct(StatesGroup):
    start_creation = State()
    step_id = State()
    step_name = State()
    step_description = State()
    step_price = State()
    step_photo = State()
