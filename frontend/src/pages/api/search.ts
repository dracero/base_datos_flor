import type { APIRoute } from 'astro';
import { searchMateriales } from '../../lib/db';

export const GET: APIRoute = async ({ url }) => {
  const q = url.searchParams.get('q') || undefined;
  const depto = url.searchParams.get('depto') || undefined;
  const periodo = url.searchParams.get('periodo') || undefined;
  const tipo = url.searchParams.get('tipo') || undefined;
  const codigoAsig = url.searchParams.get('codigoAsig') || undefined;

  try {
    const results = await searchMateriales({
      q,
      depto,
      periodo,
      tipo,
      codigoAsig,
      limit: 100
    });

    return new Response(JSON.stringify({ success: true, count: results.length, data: results }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  } catch (err: any) {
    return new Response(JSON.stringify({ success: false, error: err.message }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }
};
