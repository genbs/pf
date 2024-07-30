import { prisma } from "@/lib/prisma"
import Transactions from "./Transactions"

const TransactionsPage = async () => {
	const transactions = await prisma.transactions.findMany({
		include: {
			tags: true,
		},
	})
	const accounts = await prisma.accounts.findMany()
	const tags = await prisma.tags.findMany()

	return (
		<div className="p-4 flex flex-col gap-y-4">
			<h2>Home</h2>
			<Transactions tags={tags} accounts={accounts} transactions={transactions} />
		</div>
	)
}

export default TransactionsPage
