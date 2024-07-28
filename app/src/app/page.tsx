import { prisma } from "@/lib/prisma"
import Transactions from "./transactions/Transactions"

const Home = async () => {
	const transactions = await prisma.transactions.findMany()
	const accounts = await prisma.accounts.findMany()

	return (
		<div className="p-4 flex flex-col gap-y-4">
			<h2>Home</h2>
			<Transactions accounts={accounts} transactions={transactions} />
		</div>
	)
}

export default Home
