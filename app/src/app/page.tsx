import { prisma } from "@/lib/prisma"

const Home = async () => {
	const transactions = await prisma.transactions.findMany()

	return (
		<div className="p-4 flex flex-col gap-y-4">
			<h2>Home</h2>

			<ul className="flex flex-col gap-y-2">
				{transactions.map(transaction => (
					<li key={transaction.id}>{transaction.description}</li>
				))}
			</ul>
		</div>
	)
}

export default Home
