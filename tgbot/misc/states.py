from aiogram.dispatcher.filters.state import StatesGroup, State


class User(StatesGroup):
    untilApproved = State()
    mainMenu = State()


class AdminMenu(StatesGroup):
    adminMenu = State()


class Codecheck(StatesGroup):
    Q1 = State()


class Feedback(StatesGroup):
    confirmFeedback = State()
    getFeedback = State()


class PurchaseMono(StatesGroup):
    checkPayment = State()
    selectAddressMono = State()
    monoComplete = State()


class Purchase(StatesGroup):
    selectedProduct = State()
    selectQuantity = State()
    selectAddress = State()
    purchaseProduct = State()


class RedactProduct(StatesGroup):
    changeRedaction = State()
    changeValue = State()


class CreateProduct(StatesGroup):
    start_creation = State()
    step_id = State()
    step_name = State()
    step_description = State()
    step_price = State()
    step_photo = State()
