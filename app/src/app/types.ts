import { Prisma } from "@prisma/client"

export type Transaction = Prisma.$TransactionsPayload["scalars"]
export type Account = Prisma.$AccountsPayload["scalars"]

export const MONTHS = [
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December",
]
