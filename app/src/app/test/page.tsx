import { prisma } from "@/lib/prisma"
import Search from "./Search"

const Test = async () => {
	const transactions = await prisma.transactions.findMany()
	const accounts = await prisma.accounts.findMany()

	return (
		<div className="p-4 flex flex-col gap-y-4">
			<Search transactions={transactions} />
		</div>
	)
}

export default Test
