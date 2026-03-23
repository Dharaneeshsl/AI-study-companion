export default function Spinner() {
  return (
    <div className="flex items-center gap-2 text-sm text-gray-400">
      <span className="h-4 w-4 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
      Loading...
    </div>
  );
}
