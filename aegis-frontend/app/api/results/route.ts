import { NextResponse } from 'next/server';
import { getScanResults } from '@/lib/data';

export async function GET() {
  try {
    const results = await getScanResults();
    return NextResponse.json(results);
  } catch (error) {
    console.error('Failed to fetch results:', error);
    return NextResponse.json({ error: 'Failed to fetch results' }, { status: 500 });
  }
}
