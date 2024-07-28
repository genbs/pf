import { prisma } from "@/lib/prisma"
import YearExpenses from "./YearExpenses"

const Expenses = async () => {
	const transactions = await prisma.transactions.findMany()
	const accounts = await prisma.accounts.findMany()

	return (
		<div className="p-4 flex flex-col gap-y-4">
			<YearExpenses accounts={accounts} transactions={transactions} />
		</div>
	)
}

export default Expenses
