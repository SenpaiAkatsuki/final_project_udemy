from aiogram.dispatcher.filters.state import StatesGroup, State


class User(StatesGroup):
    untilApproved = State()
    mainMenu = State()


class AdminMenu(StatesGroup):
    adminMenu = State()


class Codecheck(StatesGroup):
    codeCheck = State()


class Feedback(StatesGroup):
    confirmFeedback = State()
    addScreenshotFeedback = State()
    sendFeedback = State()
    answerFeedback = State()
    getFeedbackAnswer = State()
    confirmFeedbackAnswer = State()


class PurchaseMono(StatesGroup):
    monoPaymentCheck = State()


class Purchase(StatesGroup):
    selectedProduct = State()
    selectQuantity = State()
    selectAddress = State()


class RedactProduct(StatesGroup):
    changeRedaction = State()
    changeValue = State()


class CreateProduct(StatesGroup):
    getProductTag = State()
    getProductTitle = State()
    getProductDescription = State()
    getProductPrice = State()
    getProductPhoto = State()


class Announcement(StatesGroup):
    getAnnouncementText = State()
    getAnnouncementPhoto = State()
    sendAnnouncement = State()
    redactAnnouncement = State()
