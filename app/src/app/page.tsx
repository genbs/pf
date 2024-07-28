import Link from "next/link"

const Home = async () => {
	return (
		<div className="p-4 flex flex-col gap-y-4">
			<Link href="/transactions">Transactions</Link>
			<Link href="/expenses">Expenses</Link>
			<Link href="/test">Test</Link>
		</div>
	)
}

export default Home
