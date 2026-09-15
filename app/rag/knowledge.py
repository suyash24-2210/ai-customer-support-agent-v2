"""
Small internal knowledge base used by the support agent.

Each article represents information that the agent is allowed
to use when answering customer questions.
"""

SUPPORT_ARTICLES = [
    {
        "id": "article_001",
        "category": "billing",
        "title": "Duplicate payment policy",
        "content": (
            "If a customer is charged more than once for the same purchase, "
            "the duplicate transaction can be reviewed for a refund. "
            "The customer's account and transaction must be verified before "
            "the refund is approved."
        ),
    },
    {
        "id": "article_002",
        "category": "billing",
        "title": "Failed payment guidance",
        "content": (
            "For failed payments, customers should first confirm that their "
            "payment method is active and that sufficient funds are available. "
            "If the issue continues, the case should be reviewed by support."
        ),
    },
    {
        "id": "article_003",
        "category": "technical",
        "title": "Application crash troubleshooting",
        "content": (
            "If the application crashes, the customer should restart the app, "
            "install the latest available version, and restart the device. "
            "Persistent crashes should be escalated for technical investigation."
        ),
    },
    {
        "id": "article_004",
        "category": "technical",
        "title": "Password reset help",
        "content": (
            "Customers who cannot reset their password should check the inbox "
            "and spam folder for the password reset email. If the reset message "
            "does not arrive, support should verify the account before further action."
        ),
    },
    {
        "id": "article_005",
        "category": "delivery",
        "title": "Order tracking information",
        "content": (
            "Customers asking about a delivery should provide their order ID. "
            "Tracking information can only be confirmed after the order has "
            "been identified."
        ),
    },
    {
        "id": "article_006",
        "category": "account",
        "title": "Locked account procedure",
        "content": (
            "A locked account requires identity verification before access can "
            "be restored. The agent should not provide account access instructions "
            "that bypass the verification process."
        ),
    },
    {
        "id": "article_007",
        "category": "account",
        "title": "Suspicious account activity",
        "content": (
            "Reports of unauthorized or suspicious account activity should be "
            "treated as high priority and escalated for human review."
        ),
    },
    {
        "id": "article_008",
        "category": "general",
        "title": "General support guidance",
        "content": (
            "If the available information does not clearly answer the customer's "
            "question, the agent should avoid guessing and request additional "
            "information or route the issue for human review."
        ),
    },
]